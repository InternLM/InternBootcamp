import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dthreereligions.Dthreereligions_reward_calculator import DthreereligionsRewardCalculator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def preprocess_nxt(s):
    n = len(s)
    nx = [-1] * 26
    nxt = [[-1] * 26 for _ in range(n + 1)]
    for i in range(n, -1, -1):
        if i < n:
            c = ord(s[i]) - ord('a')
            nx[c] = i + 1
        for j in range(26):
            nxt[i][j] = nx[j]
    return nxt

def trans(nxt, k, d):
    return -1 if k == -1 else nxt[k][d]

def better(a, b):
    if a == -1:
        return b
    if b == -1:
        return a
    return min(a, b)

def simulate_operations(s, operations):
    nxt = preprocess_nxt(s)
    dp = [[[-1 for _ in range(251)] for _ in range(251)] for __ in range(251)]
    dp[0][0][0] = 0
    st1, st2, st3 = [], [], []
    c1, c2, c3 = 0, 0, 0
    expected_outputs = []
    for op in operations:
        parts = op.split()
        cmd, id = parts[0], int(parts[1])
        if cmd == '+':
            d = ord(parts[2]) - ord('a')
            if id == 1:
                st1.append(d)
                new_c1 = c1 + 1
                for i in range(c2 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[c1][i][j], d)
                        if i > 0:
                            di = st2[i-1]
                            val = better(val, trans(nxt, dp[new_c1][i-1][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[new_c1][i][j-1], dj))
                        dp[new_c1][i][j] = val
                c1 += 1
            elif id == 2:
                st2.append(d)
                new_c2 = c2 + 1
                for i in range(c1 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[i][c2][j], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][new_c2][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[i][new_c2][j-1], dj))
                        dp[i][new_c2][j] = val
                c2 += 1
            else:
                st3.append(d)
                new_c3 = c3 + 1
                for i in range(c1 + 1):
                    for j in range(c2 + 1):
                        val = trans(nxt, dp[i][j][c3], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][j][new_c3], di))
                        if j > 0:
                            dj = st2[j-1]
                            val = better(val, trans(nxt, dp[i][j-1][new_c3], dj))
                        dp[i][j][new_c3] = val
                c3 += 1
        else:
            if id == 1:
                st1.pop()
                c1 -= 1
            elif id == 2:
                st2.pop()
                c2 -= 1
            else:
                st3.pop()
                c3 -= 1
        current_dp = dp[c1][c2][c3]
        expected_outputs.append('YES' if current_dp != -1 else 'NO')
    return expected_outputs

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DthreereligionsVerificationTool(BaseTool):
    """Dthreereligions验证工具"""
    
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
            score = DthreereligionsRewardCalculator.verify_score(
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
            logger.error(f"DthreereligionsVerificationTool执行错误: {str(e)}")
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

