import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cperfecttriples.Cperfecttriples_reward_calculator import CperfecttriplesRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CperfecttriplesVerificationTool(BaseTool):
    """Cperfecttriples验证工具"""
    
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
            score = CperfecttriplesRewardCalculator.verify_score(
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
            logger.error(f"CperfecttriplesVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def _get_st2(cls, count):
        """ 优化st2计算：通过位长度快速定位起始点 """
        if count == 0:
            return 0
        target = 3 * count
        bit_len = target.bit_length()
        exponent = (bit_len + 1) // 2  # 4^exponent初始估算
        st2 = 1 << (2 * exponent)

        # 精确调整
        while st2 > target:
            exponent -= 1
            st2 >>= 2
        while st2 * 4 <= target:
            st2 <<= 2
        return st2

    @classmethod
    def _getFirstInTriple(cls, count):
        st2 = cls._get_st2(count)
        return st2 + count - (st2 - 1) // 3 - 1

    @classmethod
    def _getValue(cls, position):
        # 保持原算法结构，优化计算效率
        triple_index = (position + 2) // 3
        first = cls._getFirstInTriple(triple_index)

        mod = position % 3
        if mod == 1:
            return first

        # 公共计算逻辑提取
        res = 0
        value = 1
        f = first
        while f > 0:
            x = f & 3
            if mod == 2:
                res += (value << 1) if x == 1 else (3*value if x ==2 else value)
            else:
                res += (3*value) if x ==1 else (value<<1 if x==3 else value)
            value <<= 2
            f >>= 2
        return res
