import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cserejaandbrackets.Cserejaandbrackets_reward_calculator import CserejaandbracketsRewardCalculator

# 导入依赖库
import random
import re
import math



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CserejaandbracketsVerificationTool(BaseTool):
    """Cserejaandbrackets验证工具"""
    
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
            score = CserejaandbracketsRewardCalculator.verify_score(
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
            logger.error(f"CserejaandbracketsVerificationTool执行错误: {str(e)}")
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
    def find_valid_regions(self, s):
        # 寻找有效括号子序列区域
        stack = []
        valid = []
        max_len = 0
        start = 0
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            else:
                if stack:
                    stack.pop()
                    if not stack:
                        valid.append((start, i))
                    else:
                        valid.append((stack[-1]+1, i))
                else:
                    start = i + 1
        return valid if valid else [(0, len(s)-1)]

    @staticmethod
    def compute_answers(s, queries):
        n = len(s)
        a = [0]*(n+1)
        for i in range(1, n+1):
            a[i] = a[i-1] + (1 if s[i-1] == '(' else -1)

        # 构建Sparse Table
        log_table = [0]*(n+2)
        for i in range(2, n+2):
            log_table[i] = log_table[i//2] + 1

        k_max = log_table[n] + 1 if n > 0 else 0
        st = [[0]*(n+1) for _ in range(k_max)]
        st[0] = a.copy()

        for k in range(1, k_max):
            for i in range(n+1 - (1 << k) + 1):
                st[k][i] = min(st[k-1][i], st[k-1][i + (1 << (k-1))])

        answers = []
        for li, ri in queries:
            l = li - 1
            r = ri
            length = r - l + 1
            k = log_table[length]
            mid = r - (1 << k) + 1

            min_val = min(st[k][l], st[k][mid])
            ans = (ri - li + 1) - (a[l] - min_val) - (a[r] - min_val)
            answers.append(max(ans // 1, 0))  # 确保结果为整数

        return answers
