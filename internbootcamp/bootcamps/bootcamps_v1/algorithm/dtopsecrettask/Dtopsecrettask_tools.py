import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dtopsecrettask.Dtopsecrettask_reward_calculator import DtopsecrettaskRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_loquacity(n, k, s, q):
    adjusted_s = min(s, (n*n)//2 + 10)  # 严格模拟参考代码的调整逻辑
    INF = float('inf')
    
    # 初始化DP数组，使用滚动数组优化
    dp = [[[INF] * (adjusted_s + 1) for _ in range(k+1)] for __ in range(2)]
    dp[0][0][0] = 0  # 初始状态

    for i in range(1, n+1):
        current = i % 2
        prev = 1 - current
        
        # 重置当前层
        for j in range(k+1):
            for t in range(adjusted_s + 1):
                dp[current][j][t] = INF
        
        # 状态转移
        for pref in range(0, min(i-1, k)+1):
            for done in range(adjusted_s + 1):
                if dp[prev][pref][done] == INF:
                    continue
                
                # 情况1：不选当前士兵
                if dp[current][pref][done] > dp[prev][pref][done]:
                    dp[current][pref][done] = dp[prev][pref][done]
                
                # 情况2：选当前士兵
                new_pref = pref + 1
                if new_pref > k:
                    continue
                
                swaps_needed = i - new_pref  # 与参考代码完全一致的计算方式
                new_done = done + swaps_needed
                
                if new_done <= adjusted_s:
                    new_value = dp[prev][pref][done] + q[i-1]
                    if new_value < dp[current][new_pref][new_done]:
                        dp[current][new_pref][new_done] = new_value
        
    # 寻找最终答案
    final_layer = n % 2
    return min(dp[final_layer][k][:adjusted_s+1])

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DtopsecrettaskVerificationTool(BaseTool):
    """Dtopsecrettask验证工具"""
    
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
            score = DtopsecrettaskRewardCalculator.verify_score(
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
            logger.error(f"DtopsecrettaskVerificationTool执行错误: {str(e)}")
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

