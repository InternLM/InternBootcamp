import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.faupontrouge.Faupontrouge_reward_calculator import FaupontrougeRewardCalculator

# 导入依赖库
import re
import math
from itertools import combinations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FaupontrougeVerificationTool(BaseTool):
    """Faupontrouge验证工具"""
    
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
            score = FaupontrougeRewardCalculator.verify_score(
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
            logger.error(f"FaupontrougeVerificationTool执行错误: {str(e)}")
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
    def find_in_trie(cls, nodes, idx):
        result = []
        cur = 0
        have = 0
        while True:
            have += nodes[cur].interm
            if have > idx:
                return ''.join(result)
            found = False
            for i in range(26):
                next_node = nodes[cur].nxt[i]
                if next_node == -1:
                    continue
                if have + nodes[next_node].have > idx:
                    result.append(chr(ord('a') + i))
                    cur = next_node
                    found = True
                    break
                else:
                    have += nodes[next_node].have
            if not found:
                break
        return ''.join(result)

    @classmethod
    def check_valid(cls, s, k, candidate, m):
        n = len(s)
        l = len(candidate)
        cont = [-1] * n

        # Precompute continuation points
        for i in range(n):
            pos = i
            while pos < n and pos - i < l and s[pos] == candidate[pos - i]:
                pos += 1
            if pos < n and pos - i < l and s[pos] < candidate[pos - i]:
                cont[i] = -1
            elif pos == n or pos - i == l:
                cont[i] = pos
            else:
                cont[i] = pos + 1 if pos < n else -1

        # DP table initialization
        dp = [[0]*m for _ in range(n)]
        if cont[0] != -1 and cont[0] <= n:
            end = cont[0] - 1
            if end < n:
                dp[end][0] = 1

        for i in range(n-1):
            for j in range(m):
                dp[i+1][j] = min(k, dp[i+1][j] + dp[i][j])

            if cont[i+1] == -1:
                continue

            for j in range(m-1):
                if dp[i][j] == 0:
                    continue
                next_pos = cont[i+1] - 1
                if next_pos >= n or j+1 >= m:
                    continue
                dp[next_pos][j+1] = min(k, dp[next_pos][j+1] + dp[i][j])

        return dp[n-1][m-1] >= k
