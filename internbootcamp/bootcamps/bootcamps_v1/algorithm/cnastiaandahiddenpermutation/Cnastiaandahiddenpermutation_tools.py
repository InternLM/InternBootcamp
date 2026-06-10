import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnastiaandahiddenpermutation.Cnastiaandahiddenpermutation_reward_calculator import CnastiaandahiddenpermutationRewardCalculator

# 导入依赖库
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnastiaandahiddenpermutationVerificationTool(BaseTool):
    """Cnastiaandahiddenpermutation验证工具"""
    
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
            score = CnastiaandahiddenpermutationRewardCalculator.verify_score(
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
            logger.error(f"CnastiaandahiddenpermutationVerificationTool执行错误: {str(e)}")
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
    def simulate_queries(self, p):
        queries = []
        n = len(p)

        def ask(t, i, j, x):
            i_index = i - 1  # Convert to 0-based
            j_index = j - 1
            pi = p[i_index]
            pj = p[j_index]
            if t == 1:
                res = max(min(x, pi), min(x + 1, pj))
            elif t == 2:
                res = min(max(x, pi), max(x + 1, pj))
            else:
                res = -1
            queries.append((t, i, j, x, res))
            return res

        a = [0] * n
        for i in range(0, n - 1, 2):
            x = ask(2, i + 1, (i + 1) + 1, 1)
            y = ask(1, i + 1, (i + 1) + 1, n - 1)

            if x == 2 and ask(1, i + 1, (i + 1) + 1, 1) == 1:
                a[i + 1] = 1
                if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                    a[i] = n
                else:
                    a[i] = y
                continue

            if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                a[i] = n
                a[i + 1] = x
                continue

            check = ask(2, (i + 1) + 1, i + 1, x)
            if check == x + 1:
                a[i] = x
                a[i + 1] = y
            else:
                a[i] = y
                a[i + 1] = x

        if n % 2 == 1:
            last = set(range(1, n + 1)) - set(a[:n-1])
            a[-1] = last.pop()

        return queries
