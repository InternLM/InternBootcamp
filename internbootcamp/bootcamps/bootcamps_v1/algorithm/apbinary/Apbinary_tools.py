import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.apbinary.Apbinary_reward_calculator import ApbinaryRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ApbinaryVerificationTool(BaseTool):
    """Apbinary验证工具"""
    
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
            score = ApbinaryRewardCalculator.verify_score(
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
            logger.error(f"ApbinaryVerificationTool执行错误: {str(e)}")
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
    def _generate_edge_case(self):  # 修正：添加正确的缩进
        """生成边界测试案例"""
        edge_types = [
            {'p': 0},  # 常规二进制
            {'p': -1000, 'n': 10**9},  # 最小p值
            {'p': 1000, 'n': 1},       # 无解情况
            {'n': 1, 'p': 1},          # 样例5
            {'p': -1, 'n': 2**20 + 1}  # 大数值案例
        ]
        case = random.choice(edge_types)
        p = case.get('p', random.randint(-1000, 1000))
        n = case.get('n', random.randint(1, 10**9))
        return {'n': n, 'p': p}

    @staticmethod
    def solve(n, p):
        if p == 0:  # 优化常规二进制情况
            if (n & (n-1)) == 0:
                return 1
            return bin(n).count('1')

        max_i = 10**6 if p < 0 else min(10**6, n//abs(p)+2)
        for i in range(1, max_i+1):
            s = n - p * i
            if s <= 0:
                continue
            if s.bit_length() > 60:  # 处理极大数值溢出
                continue
            if bin(s).count('1') <= i and s >= i:
                return i
        return -1
