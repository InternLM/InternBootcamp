import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccoloringtrees.Ccoloringtrees_reward_calculator import CcoloringtreesRewardCalculator

# 导入依赖库
import json
import random
import re

# === 源文件中的全局函数 ===

def solve(n, m, k, c_list, p_matrix):
    INF = 10**18
    c = c_list
    p = p_matrix

    # DP优化算法实现
    dp = [[INF]*(m+1) for _ in range(k+1)]
    dp[0][0] = 0  # 初始状态
    
    for tree_idx in range(n):
        current_color = c[tree_idx]
        new_dp = [[INF]*(m+1) for _ in range(k+1)]
        
        for groups in range(k+1):
            for prev_color in range(m+1):
                if dp[groups][prev_color] == INF:
                    continue
                
                for new_color in range(1, m+1):
                    if current_color != 0 and current_color != new_color:
                        continue  # 已染色树不能改变颜色
                    
                    # 计算新分组数
                    new_groups = groups + (1 if new_color != prev_color else 0)
                    if new_groups > k:
                        continue
                    
                    # 计算成本
                    cost = p[tree_idx][new_color-1] if current_color == 0 else 0
                    
                    new_dp[new_groups][new_color] = min(
                        new_dp[new_groups][new_color],
                        dp[groups][prev_color] + cost
                    )
        
        dp = new_dp

    min_cost = min(dp[k][color] for color in range(1, m+1))
    return min_cost if min_cost < INF else -1

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcoloringtreesVerificationTool(BaseTool):
    """Ccoloringtrees验证工具"""
    
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
            score = CcoloringtreesRewardCalculator.verify_score(
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
            logger.error(f"CcoloringtreesVerificationTool执行错误: {str(e)}")
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

