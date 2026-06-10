import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.aalmostarithmeticalprogression.Aalmostarithmeticalprogression_reward_calculator import AalmostarithmeticalprogressionRewardCalculator

# 导入依赖库
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class AalmostarithmeticalprogressionVerificationTool(BaseTool):
    """Aalmostarithmeticalprogression验证工具"""
    
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
            score = AalmostarithmeticalprogressionRewardCalculator.verify_score(
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
            logger.error(f"AalmostarithmeticalprogressionVerificationTool执行错误: {str(e)}")
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
        """生成边界测试用例（全相同元素、交替元素等）"""
        case_type = random.choice([
            'all_same', 
            'alternating',
            'single_element'
        ])

        if case_type == 'all_same':
            n = random.randint(1, self.max_n)
            val = random.randint(self.min_val, self.max_val)
            return {
                "n": n,
                "b": [val]*n,
                "ans": n
            }

        elif case_type == 'alternating':
            n = random.randint(2, self.max_n)
            a, b = random.sample(range(self.min_val, self.max_val+1), 2)
            return {
                "n": n,
                "b": [a, b]*(n//2) + [a]*(n%2),
                "ans": n
            }

        else:  # single_element
            return {
                "n": 1,
                "b": [random.randint(self.min_val, self.max_val)],
                "ans": 1
            }

    def _generate_standard_case(self):
        """标准案例生成逻辑改进"""
        # 构造有效AAP序列
        base_len = random.randint(3, self.max_n)
        aap = self._generate_valid_aap(base_len)

        # 插入噪声元素
        noise_num = random.randint(0, self.max_n - base_len)
        b = self._insert_noise(aap, noise_num)
        random.shuffle(b)  # 保持子序列顺序但不要求连续

        return {
            "n": len(b),
            "b": b,
            "ans": self.calculate_max_aap_length(b)
        }

    def _generate_valid_aap(self, length):
        """生成符合AAP定义的基准序列"""
        p = random.randint(self.min_val, self.max_val)
        q = random.randint(1, (self.max_val - self.min_val)//2)
        sequence = [p]
        for i in range(1, length):
            sign = (-1)**(i+1)
            sequence.append(sequence[i-1] + sign * q)
        return sequence

    def _insert_noise(self, base, noise_num):
        """随机插入噪声元素"""
        for _ in range(noise_num):
            insert_pos = random.randint(0, len(base))
            base.insert(insert_pos, random.randint(self.min_val, self.max_val))
        return base

    @staticmethod
    def calculate_max_aap_length(b):
        """精确实现原题解算法"""
        n = len(b)
        if n <= 1:
            return n

        max_len = 1
        dp = defaultdict(lambda: defaultdict(int))

        for i in range(n):
            for j in range(i+1, n):
                key = (b[i], b[j] - ((-1)**(2+1)) * (b[j] - b[i]))
                dp[j][key] = max(dp[j].get(key, 0), dp[i].get(key, 1) + 1)
                max_len = max(max_len, dp[j][key])

        return max(max_len, 2 if n >=2 else 1)
