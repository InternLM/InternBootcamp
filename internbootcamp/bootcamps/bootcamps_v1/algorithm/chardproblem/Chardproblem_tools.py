import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chardproblem.Chardproblem_reward_calculator import ChardproblemRewardCalculator

# 导入依赖库
import random
import string
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ChardproblemVerificationTool(BaseTool):
    """Chardproblem验证工具"""
    
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
            score = ChardproblemRewardCalculator.verify_score(
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
            logger.error(f"ChardproblemVerificationTool执行错误: {str(e)}")
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
    def _generate_strings_with_edge_cases(self, n):
        """生成包含前缀、相同字符串等边界情况的序列"""
        strings = []
        if random.random() < 0.3:
            base = self._random_string()
            strings.append(base)
            for _ in range(n-1):
                strings.append(base + self._random_string(1))
        elif random.random() < 0.3: 
            s = self._random_string()
            strings = [s] * n
        else:
            total_length = 0
            for _ in range(n):
                max_len = min(self.max_string_length, 100000 - total_length)
                if max_len <=0:
                    s = ''
                else:
                    length = random.randint(1, max_len)
                    s = ''.join(random.choices(string.ascii_lowercase, k=length))
                    total_length += length
                strings.append(s)
        return strings

    def _random_string(self, length=None):
        """生成随机长度的字符串"""
        if length is None:
            length = random.randint(1, self.max_string_length)
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _solve_case(self, n, c, strings):
        """动态规划求解正确结果 (完整实现)"""
        dp = [[-1] * 2 for _ in range(n)]
        dp[0][0] = 0
        dp[0][1] = c[0]
        possible = True

        for i in range(1, n):
            prev = strings[i-1]
            current = strings[i]
            prev_rev = prev[::-1]
            current_rev = current[::-1]

            dp_i0 = -1
            dp_i1 = -1

            # 处理不反转当前字符串的情况
            if dp[i-1][0] != -1 and current >= prev:
                dp_i0 = dp[i-1][0]
            if dp[i-1][1] != -1 and current >= prev_rev:
                if dp_i0 == -1 or dp[i-1][1] < dp_i0:
                    dp_i0 = dp[i-1][1]

            # 处理反转当前字符串的情况
            cost = c[i]
            if dp[i-1][0] != -1 and current_rev >= prev:
                dp_i1 = dp[i-1][0] + cost
            if dp[i-1][1] != -1 and current_rev >= prev_rev:
                candidate = dp[i-1][1] + cost
                if dp_i1 == -1 or candidate < dp_i1:
                    dp_i1 = candidate

            dp[i][0] = dp_i0
            dp[i][1] = dp_i1

            if dp[i][0] == -1 and dp[i][1] == -1:
                possible = False
                break

        if not possible:
            return -1

        final0 = dp[-1][0]
        final1 = dp[-1][1]
        if final0 == -1 and final1 == -1:
            return -1
        return min(filter(lambda x: x != -1, [final0, final1])) if final0 != -1 and final1 != -1 else max(final0, final1)
