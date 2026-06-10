import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnezzarandsymmetricarray.Cnezzarandsymmetricarray_reward_calculator import CnezzarandsymmetricarrayRewardCalculator

# 导入依赖库
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnezzarandsymmetricarrayVerificationTool(BaseTool):
    """Cnezzarandsymmetricarray验证工具"""
    
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
            score = CnezzarandsymmetricarrayRewardCalculator.verify_score(
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
            logger.error(f"CnezzarandsymmetricarrayVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_case(self, n):
        min_val, max_val = self.value_range
        positives = []
        while len(positives) < n:
            num = random.randint(min_val, max_val)
            if num not in positives:
                positives.append(num)

        symmetric_array = []
        for num in positives:
            symmetric_array.extend([num, -num])
        random.shuffle(symmetric_array)

        d_array = [sum(abs(num - other) for other in symmetric_array) for num in symmetric_array]
        return {'n': n, 'd': d_array}

    def _generate_robust_invalid_case(self, n, max_attempts=10):
        # 策略1：破坏有效案例的约束条件
        for _ in range(max_attempts):
            valid_case = self._generate_valid_case(n)
            d = valid_case['d'].copy()
            sorted_d = sorted(d)

            # 破坏方法1：打破配对约束
            last_pair_index = 2*n - 2
            if sorted_d[last_pair_index] == sorted_d[last_pair_index + 1]:
                sorted_d[-1] += 1
                shuffled = sorted_d.copy()
                random.shuffle(shuffled)
                if self.check_case(n, shuffled) == 'NO':
                    return {'n': n, 'd': shuffled}

            # 破坏方法2：修改数值导致余数错误
            target_index = random.choice(range(0, 2*n, 2))
            sorted_d[target_index] += 2*n
            shuffled = sorted_d.copy()
            random.shuffle(shuffled)
            if self.check_case(n, shuffled) == 'NO':
                return {'n': n, 'd': shuffled}

        # 策略2：完全随机生成直至找到无效案例
        for _ in range(max_attempts):
            random_d = [random.randint(0, 10**6) for _ in range(2*n)]
            if self.check_case(n, random_d) == 'NO':
                return {'n': n, 'd': random_d}

        # 保底策略：构造必定失败的案例
        return {'n': n, 'd': [0]*(2*n)}

    @staticmethod
    def check_case(n, d_list):
        sorted_d = sorted(d_list)
        su = 0
        current_n = n
        valid = True

        if len(sorted_d) != 2*current_n:
            return 'NO'

        while current_n > 0 and valid:
            i = 2*current_n - 1
            if i < 1 or sorted_d[i] != sorted_d[i-1]:
                valid = False
                break

            if i > 1 and sorted_d[i] == sorted_d[i-2]:
                valid = False
                break

            total = sorted_d[i] - 2*su
            if total % (2*current_n) != 0:
                valid = False
                break

            cur = total // (2*current_n)
            if cur <= 0:
                valid = False
                break

            su += cur
            current_n -= 1

        return 'YES' if valid and current_n == 0 else 'NO'
