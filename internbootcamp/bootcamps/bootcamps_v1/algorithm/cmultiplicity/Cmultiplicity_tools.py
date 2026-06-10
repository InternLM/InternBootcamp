import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmultiplicity.Cmultiplicity_reward_calculator import CmultiplicityRewardCalculator

# 导入依赖库
import math
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

factor_cache = FactorCache()



# === 源文件中的全局函数 ===

def compute_answer(n, a):
    """完全重构的动态规划解法"""
    dp = defaultdict(int)
    dp[0] = 1  # 初始状态：空序列
    total = 0
    
    for num in a:
        factors = sorted(factor_cache.get_factors(num), reverse=True)
        for f in factors:
            if f == 0:
                continue
            prev = f - 1
            if prev in dp:
                contribution = dp[prev]
                total = (total + contribution) % MOD
                dp[f] = (dp[f] + contribution) % MOD
                
    return total



# === 源文件中的其他类 ===

class FactorCache:
    """优化后的因数缓存机制"""
    def __init__(self):
        self.cache = defaultdict(set)
    
    def get_factors(self, n):
        if n not in self.cache:
            factors = set()
            if n > 0:
                max_factor = int(math.isqrt(n))
                step = 2 if n % 2 else 1
                for i in range(1, max_factor + 1, step):
                    if n % i == 0:
                        factors.add(i)
                        factors.add(n//i)
            self.cache[n] = factors
        return self.cache[n]

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmultiplicityVerificationTool(BaseTool):
    """Cmultiplicity验证工具"""
    
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
            score = CmultiplicityRewardCalculator.verify_score(
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
            logger.error(f"CmultiplicityVerificationTool执行错误: {str(e)}")
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

