import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.erememberingstrings.Erememberingstrings_reward_calculator import ErememberingstringsRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ErememberingstringsVerificationTool(BaseTool):
    """Erememberingstrings验证工具"""
    
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
            score = ErememberingstringsRewardCalculator.verify_score(
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
            logger.error(f"ErememberingstringsVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_case(self, n, m):
        # 生成目标字符串：每个字符串至少有一个唯一特征位
        target_strings = []
        pos_pool = list(range(m)) * ((n // m) + 1)
        random.shuffle(pos_pool)

        for i in range(n):
            s = ['x'] * m
            unique_pos = pos_pool[i]
            # 确保该位置字符唯一
            used_chars = set()
            for ts in target_strings:
                used_chars.add(ts[unique_pos])
            while True:
                c = random.choice('abcdefghijklmnopqrstuvwxyz')
                if c not in used_chars:
                    s[unique_pos] = c
                    break
            # 其他位置随机生成
            for j in range(m):
                if j != unique_pos:
                    s[j] = random.choice('abcdefghijklmnopqrstuvwxyz')
            target_strings.append(''.join(s))

        # 构造原始字符串（通过修改目标字符串得到）
        original_strings = []
        cost_matrix = []
        for idx, target in enumerate(target_strings):
            original = list(target)
            modify_pos = random.sample(range(m), k=random.randint(0, m//2))
            costs = []
            for j in range(m):
                if j in modify_pos:
                    # 生成修改成本并改变字符
                    original[j] = random.choice('abcdefghijklmnopqrstuvwxyz'.replace(target[j], ''))
                    costs.append(random.randint(1, 1000))
                else:
                    costs.append(0)
            original_strings.append(''.join(original))
            cost_matrix.append(costs)

        return original_strings, cost_matrix

    @staticmethod
    def calculate_min_cost(n, m, strings, cost_matrix):
        INF = float('inf')
        dp = [INF] * (1 << n)
        dp[0] = 0

        for state in range(1 << n):
            if dp[state] == INF:
                continue

            # Find first unset bit
            bit = None
            for i in range(n):
                if not (state & (1 << i)):
                    bit = i
                    break
            if bit is None:
                continue

            # Try all possible positions
            for j in range(m):
                # Option 1: change current string's j-th character
                new_state = state | (1 << bit)
                cost = dp[state] + cost_matrix[bit][j]
                if dp[new_state] > cost:
                    dp[new_state] = cost

                # Option 2: group change
                same_chars = [bit]
                for k in range(n):
                    if k != bit and strings[k][j] == strings[bit][j]:
                        same_chars.append(k)

                sum_cost = sum(cost_matrix[x][j] for x in same_chars)
                max_cost = max(cost_matrix[x][j] for x in same_chars)
                total_cost = sum_cost - max_cost
                new_state_group = state
                for x in same_chars:
                    new_state_group |= (1 << x)

                if dp[new_state_group] > dp[state] + total_cost:
                    dp[new_state_group] = dp[state] + total_cost

        return dp[(1 << n) - 1]
