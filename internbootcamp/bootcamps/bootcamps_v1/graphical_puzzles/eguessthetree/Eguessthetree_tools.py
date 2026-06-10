import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.eguessthetree.Eguessthetree_reward_calculator import EguessthetreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EguessthetreeVerificationTool(BaseTool):
    """Eguessthetree验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = EguessthetreeRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"EguessthetreeVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法
    def _generate_initial_n(self, yes_case):
        if yes_case:
            return random.choice([n for n in range(self.min_n, self.max_n+1) if n ==1 or n>=3])
        return random.randint(self.min_n, self.max_n)

    def _generate_valid_case(self, n):
        if n == 1:
            return {'n':1, 'c':[1], 'expected_answer':'YES'}

        # 生成符合约束的树结构
        root = n
        children = self._split_subtrees(n-1)
        c = [root] + children
        random.shuffle(c)
        return {'n':n, 'c':c, 'expected_answer':'YES'}

    def _split_subtrees(self, total):
        if total == 0:
            return []
        if total == 1:
            return [1]

        # 至少分割为两个子树且每个>=1
        k = random.randint(2, total)
        parts = []
        while sum(parts) < total:
            remain = total - sum(parts)
            max_part = min(remain - (k - len(parts) - 1), remain)
            part = random.randint(1, max_part)
            parts.append(part)

        # 确保内部节点有足够子节点
        return [p if p >=2 else 1 for p in parts]

    def _generate_invalid_case(self, n):
        for _ in range(100):
            # 类型1: 缺少根节点
            if random.random() < 0.5:
                c = [random.randint(1, n-1) for _ in range(n)]
                if n not in c:
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

            # 类型2: 存在根节点但结构冲突
            else:
                c = [n] + random.choices([1,1,2,3], k=n-1)
                if not self._is_valid_solution(n, c):
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

        return {'n':2, 'c':[1,1], 'expected_answer':'NO'}

    def _is_valid_solution(self, n, c):
        # 快速预检查
        if sum(c) != n*(n+1)//2 and n > 1:  # 修正总和验证逻辑
            return False

        # 完整回溯验证
        avail = defaultdict(int)
        for num in c:
            if num > n:
                return False
            avail[num] += 1

        try:
            self._backtrack(avail, [], sum(c), n)
            return False
        except self.SolutionFound:
            return True

    def _backtrack(self, avail, stack, sumleft, n):
        if not stack and sumleft == 0:
            raise self.SolutionFound()

        # 添加叶子节点分支
        if avail[1] > 0:
            avail[1] -= 1
            self._backtrack(avail, stack + [1], sumleft - 1, n)
            avail[1] += 1

        # 合并子树分支
        if len(stack) >= 2:
            s = 0
            for i in range(1, len(stack)+1):
                s += stack[-i]
                if s > n:
                    break
                if avail[s] > 0:
                    avail[s] -= 1
                    self._backtrack(avail, stack[:-i] + [s], sumleft - s, n)
                    avail[s] += 1
