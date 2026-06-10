import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.ccandiesdistribution.Ccandiesdistribution_reward_calculator import CcandiesdistributionRewardCalculator

# 导入依赖库
import random
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcandiesdistributionVerificationTool(BaseTool):
    """Ccandiesdistribution验证工具"""
    
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
            score = CcandiesdistributionRewardCalculator.verify_score(
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
            logger.error(f"CcandiesdistributionVerificationTool执行错误: {str(e)}")
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
    def generate_valid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        a = []

        # 生成策略优化
        if case_type == 'valid_standard':
            # 使用拓扑排序生成合法案例
            graph = [[] for _ in range(n)]
            in_degree = [0]*n
            q = deque()

            # 构造约束关系
            for i in range(n):
                for j in range(i+1, n):
                    if random.random() < 0.3:
                        graph[i].append(j)
                        in_degree[j] += 1
                    else:
                        graph[j].append(i) 
                        in_degree[i] += 1

            # 拓扑排序生成合法值
            while q:
                u = q.popleft()
                a.append(random.randint(1, n))
                for v in graph[u]:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        q.append(v)
            a += [random.randint(1, n) for _ in range(n - len(a))]
        else:  # valid_duplicates
            base = random.randint(1, n//2)
            a = [base + i % 3 for i in range(n)]
            random.shuffle(a)

        # 计算合法约束
        l = [sum(a[j] > a[i] for j in range(i)) for i in range(n)]
        r = [sum(a[j] > a[i] for j in range(i+1, n)) for i in range(n)]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': True,
            'type': case_type
        }

    def generate_invalid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        l = [0]*n
        r = [0]*n

        if case_type == 'invalid_boundary':
            # 边界条件无效：首位儿童左边有人，末位儿童右边有人
            targets = [0, n-1] if n > 1 else [0]
            for i in targets:
                if i == 0:
                    l[i] = random.randint(1, 3)
                else:
                    r[i] = random.randint(1, 3)

        elif case_type == 'invalid_overflow':
            # 数值超限：单个值超过理论最大值
            i = random.randint(0, n-1)
            max_possible = i if i < n-1 else 0
            l[i] = max_possible + random.randint(1, 2)

        elif case_type == 'invalid_sum':
            # 总和矛盾：l_i + r_i > 可能的最大值
            i = random.randint(0, n-1)
            max_total = (n - 1) - (i + (n - i - 1))
            if max_total < 0: max_total = 0
            current_sum = random.randint(max_total + 1, max_total + 3)
            l[i] = current_sum // 2
            r[i] = current_sum - l[i]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': False,
            'type': case_type
        }
