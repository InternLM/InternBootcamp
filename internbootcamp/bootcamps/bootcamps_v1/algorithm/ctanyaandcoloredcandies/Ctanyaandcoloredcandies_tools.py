import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctanyaandcoloredcandies.Ctanyaandcoloredcandies_reward_calculator import CtanyaandcoloredcandiesRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_candy_boxes(n, s, k, r_list, color_str):
    s -= 1  # 转换为0-based索引
    r = r_list
    color = color_str
    INF = float('inf')
    
    # 预处理最大可能的糖果数
    max_possible = sum(r)
    if max_possible < k:
        return -1
    
    # 动态规划数组，dp[cur][c]表示从cur出发，获得至少c颗糖果的最短时间
    dp = [[INF] * (k + 1) for _ in range(n)]
    
    # 预处理每个盒子自身的情况
    for i in range(n):
        current_max = min(r[i], k)
        for c in range(current_max + 1):
            dp[i][c] = 0  # 只需要吃当前盒子即可
        
    # 记忆化搜索函数
    def dfs(cur):
        # 已经处理过的情况直接返回
        if dp[cur][k] != INF:
            return
        
        # 尝试所有可能的后继盒子
        for to in range(n):
            if color[to] != color[cur] and r[to] > r[cur]:
                dfs(to)
                distance = abs(cur - to)
                
                # 状态转移：当前吃掉的糖果数 + 后续吃掉的糖果数
                for c in range(k, -1, -1):
                    if dp[cur][c] == INF:
                        continue
                    
                    # 计算转移后的糖果数
                    new_c = min(c + r[to], k)
                    cost = dp[cur][c] + distance
                    if cost < dp[to][new_c]:
                        dp[to][new_c] = cost
                        # 回溯更新所有可能的更优解
                        for nc in range(new_c, k+1):
                            if dp[to][nc] > cost:
                                dp[to][nc] = cost
    
    # 从每个可能的起点开始计算
    for i in range(n):
        dfs(i)
    
    # 计算最小时间
    min_time = INF
    for i in range(n):
        start_cost = abs(i - s)
        if start_cost + dp[i][k] < min_time:
            min_time = start_cost + dp[i][k]
    
    return min_time if min_time != INF else -1

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CtanyaandcoloredcandiesVerificationTool(BaseTool):
    """Ctanyaandcoloredcandies验证工具"""
    
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
            score = CtanyaandcoloredcandiesRewardCalculator.verify_score(
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
            logger.error(f"CtanyaandcoloredcandiesVerificationTool执行错误: {str(e)}")
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

