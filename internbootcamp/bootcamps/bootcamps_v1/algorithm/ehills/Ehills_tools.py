import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ehills.Ehills_reward_calculator import EhillsRewardCalculator

# 导入依赖库
import math
import random
from typing import List

# === 源文件中的全局函数 ===

def compute_min_time(n: int, a_list: List[int]) -> List[int]:
    INF = float('inf')
    high = [-INF] + a_list.copy() + [-INF]
    m = math.ceil(n / 2)
    
    # 初始化DP表，使用二维列表表示当前j和状态0/1/2的最小时间
    dp = [[INF] * 3 for _ in range(m + 1)]
    dp[0][0] = 0  # 初始状态：0个峰，最后状态是0（未选）
    
    for i in range(1, n + 1):
        new_dp = [[INF] * 3 for _ in range(m + 1)]
        for j in range(m + 1):
            for state in range(3):
                if dp[j][state] == INF:
                    continue
                
                if state == 0:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，转移到状态1
                    if j < m:
                        cost = 0
                        if high[i] <= high[i - 1]:
                            cost += high[i - 1] - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
                
                elif state == 1:
                    # 当前必须不选i（连续不能选），转移到状态2
                    new_dp[j][2] = min(new_dp[j][2], dp[j][state])
                
                elif state == 2:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，需考虑前前一个峰的影响
                    if j < m:
                        cost = 0
                        prev_peak_height = high[i - 1]
                        # 考虑i-2的影响
                        if i >= 2 and high[i - 2] <= prev_peak_height:
                            prev_peak_height = high[i - 2] - 1
                        # 计算当前i需要调整的高度
                        if high[i] <= prev_peak_height:
                            cost += prev_peak_height - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
        dp = new_dp
    
    # 收集结果
    result = []
    for k in range(1, m + 1):
        min_val = min(dp[k][0], dp[k][1], dp[k][2])
        result.append(min_val if min_val != INF else 0)
    return result

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EhillsVerificationTool(BaseTool):
    """Ehills验证工具"""
    
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
            score = EhillsRewardCalculator.verify_score(
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
            logger.error(f"EhillsVerificationTool执行错误: {str(e)}")
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

