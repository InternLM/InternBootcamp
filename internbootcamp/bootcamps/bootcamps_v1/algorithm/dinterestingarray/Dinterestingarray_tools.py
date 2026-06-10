import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dinterestingarray.Dinterestingarray_reward_calculator import DinterestingarrayRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DinterestingarrayVerificationTool(BaseTool):
    """Dinterestingarray验证工具"""
    
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
            score = DinterestingarrayRewardCalculator.verify_score(
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
            logger.error(f"DinterestingarrayVerificationTool执行错误: {str(e)}")
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
    def _generate_solvable_case(self, n, m):
        """生成必定有解的案例"""
        a = [random.randint(0, self.qi_max) for _ in range(n)]
        constraints = []
        for _ in range(m-1):
            l = random.randint(1, n)
            r = random.randint(l, n)
            current_and = a[l-1]
            for i in range(l, r):
                current_and &= a[i]
            constraints.append((l, r, current_and))

        # 添加全局约束保证解存在
        constraints.append((1, n, current_and))
        return {
            'n': n,
            'm': m,
            'constraints': constraints,
            'solution_exists': True,
            'possible_a': a
        }

    def _add_conflict_constraint(self, case):
        """添加矛盾约束"""
        # 复制原有约束
        new_constraints = case['constraints'][:]
        l, r = self._find_overlap_interval(new_constraints)

        # 生成矛盾的约束值
        original_q = new_constraints[0][2]
        conflict_q = original_q ^ (1 << random.randint(0, self.bit_width-1))

        # 添加新约束
        new_constraints.append((l, r, conflict_q))
        return {
            'n': case['n'],
            'm': case['m'] + 1,
            'constraints': new_constraints
        }

    def _find_overlap_interval(self, constraints):
        """找到多个约束的重叠区间"""
        intervals = [(l, r) for l, r, _ in constraints]
        max_l = max(l for l, _ in intervals)
        min_r = min(r for _, r in intervals)
        if max_l <= min_r:
            return (max_l, min_r)
        return (1, constraints[0][0])  # 默认返回第一个约束的区间

    def _validate_case(self, case):
        """科学校验案例有效性"""
        n = case['n']
        constraints = case['constraints']

        # 初始化各bit位的允许范围
        bit_masks = [0xFFFFFFFF for _ in range(n)]

        # 应用所有约束
        for l, r, q in constraints:
            for i in range(l-1, r):
                bit_masks[i] &= q

        # 检查所有位置是否可能
        for i in range(n):
            if bit_masks[i] == 0 and not any(
                (l-1 <= i <= r-1 and q == 0) 
                for l, r, q in constraints
            ):
                return False, None

        # 验证约束一致性
        for l, r, q in constraints:
            required_bits = q
            possible_and = 0xFFFFFFFF
            for i in range(l-1, r):
                possible_and &= bit_masks[i]
            if (possible_and & required_bits) != required_bits:
                return False, None

        # 构造可行解
        solution = [random.randint(0, mask) & mask for mask in bit_masks]
        return True, solution
