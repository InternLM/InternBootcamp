import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdevelopingskills.Cdevelopingskills_reward_calculator import CdevelopingskillsRewardCalculator

# 导入依赖库
import random
import re
import math



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CdevelopingskillsVerificationTool(BaseTool):
    """Cdevelopingskills验证工具"""
    
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
            score = CdevelopingskillsRewardCalculator.verify_score(
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
            logger.error(f"CdevelopingskillsVerificationTool执行错误: {str(e)}")
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
    def _generate_edge_case(self):
        case_type = random.choice([
            'max_skills', 'zero_improvements', 'all_maxed', 
            'large_k', 'minimum_values'
        ])

        if case_type == 'max_skills':
            return {
                'n': self.max_n,
                'k': self.max_k,
                'a_list': [100] * self.max_n,
                'correct_output': 10 * self.max_n
            }
        elif case_type == 'zero_improvements':
            a_list = [random.randint(0, 100) for _ in range(random.randint(1, self.max_n))]
            return {
                'n': len(a_list),
                'k': 0,
                'a_list': a_list,
                'correct_output': sum(x//10 for x in a_list)
            }
        elif case_type == 'all_maxed':
            n = random.randint(1, self.max_n)
            return {
                'n': n,
                'k': random.randint(0, self.max_k),
                'a_list': [100]*n,
                'correct_output': 10*n
            }
        elif case_type == 'large_k':
            n = random.randint(1, 100)
            return {
                'n': n,
                'k': 10**7,
                'a_list': [0]*n,
                'correct_output': min(10*n, (sum(0//10 for _ in range(n)) + 10**7//10))
            }
        else:
            return {
                'n': 1,
                'k': 0,
                'a_list': [0],
                'correct_output': 0
            }

    @staticmethod
    def _calculate_solution(n, k, a_list):
        total = sum(x // 10 for x in a_list)
        remainder_counts = [0] * 10  # 索引对应delta值1-9（0位置不使用）

        for x in a_list:
            rem = x % 10
            if rem != 0:
                delta = 10 - rem
                if 1 <= delta <= 9:
                    remainder_counts[delta] += 1

        # 按delta从大到小处理（9到1）
        for delta in range(9, 0, -1):
            if k <= 0:
                break
            count = remainder_counts[delta]
            if count == 0:
                continue

            max_possible = min(k // delta, count)
            total += max_possible
            k -= max_possible * delta

        # 处理剩余k值
        total += k // 10
        return min(total, 10 * n)
