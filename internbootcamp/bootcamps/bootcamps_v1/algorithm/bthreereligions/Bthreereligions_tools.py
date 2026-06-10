import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bthreereligions.Bthreereligions_reward_calculator import BthreereligionsRewardCalculator

# 导入依赖库
import random
import re
from typing import List
from typing import Dict
from typing import Any



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BthreereligionsVerificationTool(BaseTool):
    """Bthreereligions验证工具"""
    
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
            score = BthreereligionsRewardCalculator.verify_score(
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
            logger.error(f"BthreereligionsVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def get_expected_outputs(word: str, operations: List[str]) -> List[str]:
        n = len(word)
        nxt = [[n+1]*(n+2) for _ in range(26)]
        for i in range(n-1, -1, -1):
            c = ord(word[i]) - ord('a')
            nxt[c][i] = i
        for c in range(26):
            for j in range(n-1, -1, -1):
                if nxt[c][j] == n+1:
                    nxt[c][j] = nxt[c][j+1]
        dp = [[[n+1 for _ in range(251)] for __ in range(251)] for ___ in range(251)]
        dp[0][0][0] = 0
        l = [0, 0, 0]
        t = ['', '', '']
        expected_outputs = []
        for op in operations:
            parts = op.split()
            if parts[0] == '+':
                religion = int(parts[1]) - 1
                c = parts[2]
                t[religion] += c
                l[religion] += 1
                lim = [0, 0, 0]
                lim[religion] = l[religion]
                for i in range(lim[0], l[0]+1):
                    for j in range(lim[1], l[1]+1):
                        for k in range(lim[2], l[2]+1):
                            if i + j + k == 0:
                                continue
                            current_min = n+1
                            if i > 0:
                                pos = dp[i-1][j][k]
                                if pos <= n:
                                    char = t[0][i-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            if j > 0:
                                pos = dp[i][j-1][k]
                                if pos <= n:
                                    char = t[1][j-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            if k > 0:
                                pos = dp[i][j][k-1]
                                if pos <= n:
                                    char = t[2][k-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            dp[i][j][k] = current_min
            else:
                religion = int(parts[1]) - 1
                t[religion] = t[religion][:-1]
                l[religion] -= 1
            current_dp = dp[l[0]][l[1]][l[2]]
            expected_outputs.append("YES" if current_dp <= n else "NO")
        return expected_outputs
