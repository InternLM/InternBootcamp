import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.asavethenature.Asavethenature_reward_calculator import AsavethenatureRewardCalculator

# 导入依赖库
import math
import random

# === 源文件中的全局函数 ===

def solve(n, p_list, x, a, y, b, k):
    arr = sorted(p_list, reverse=True)
    # 确保x是较大值并交换参数
    if y > x:
        x, y = y, x
        a, b = b, a
    
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    g = gcd(a, b)
    lcm_ab = (a * b) // g if g != 0 else 0
    lo = 0
    hi = n
    
    while lo < hi:
        mid = (lo + hi) // 2
        cnt1 = mid // lcm_ab if lcm_ab != 0 else 0
        cnt2 = mid // a - cnt1
        cnt3 = mid // b - cnt1
        
        total = 0
        ind = 0
        # 处理x+y%的贡献
        for _ in range(cnt1):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * (x + y)
            ind += 1
        # 处理x%的贡献
        for _ in range(cnt2):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * x
            ind += 1
        # 处理y%的贡献
        for _ in range(cnt3):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * y
            ind += 1
        
        if total >= k:
            hi = mid
        else:
            lo = mid + 1
    
    return lo if lo <= n else -1  # 移除多余验证

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class AsavethenatureVerificationTool(BaseTool):
    """Asavethenature验证工具"""
    
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
            score = AsavethenatureRewardCalculator.verify_score(
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
            logger.error(f"AsavethenatureVerificationTool执行错误: {str(e)}")
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

