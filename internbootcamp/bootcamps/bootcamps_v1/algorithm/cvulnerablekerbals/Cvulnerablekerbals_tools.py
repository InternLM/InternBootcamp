import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cvulnerablekerbals.Cvulnerablekerbals_reward_calculator import CvulnerablekerbalsRewardCalculator

# 导入依赖库
import re
import math
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def exgcd(a, b):
    if b == 0:
        return (a, 1, 0)
    else:
        g, x, y = exgcd(b, a % b)
        return (g, y, x - (a // b) * y)

def generate_solution_for_m(m):
    vis = set()
    g = defaultdict(list)
    for i in range(m):
        if i not in vis:
            g_val = math.gcd(i, m)
            g[g_val].append(i)
    
    divisors = [d for d in range(1, m + 1) if m % d == 0]
    divisors.sort()
    
    dp = {d: 0 for d in divisors}
    pre = {d: None for d in divisors}
    
    for d in divisors:
        dp[d] = len(g.get(d, []))
        j = 2 * d
        while j <= m:
            if j not in divisors:
                j += d
                continue
            if dp[j] < dp[d]:
                dp[j] = dp[d]
                pre[j] = d
            elif dp[j] == dp[d]:
                if pre[j] is None or pre[j] < d:
                    pre[j] = d
            j += d
    
    current_d = m
    w = []
    while True:
        w.extend(g.get(current_d, []))
        if current_d == 1:
            break
        current_d = pre.get(current_d)
        if current_d is None:
            break
    
    if not w:
        return 0, []
    
    sequence = []
    sequence.append(w[-1])
    for i in range(len(w)-1, 0, -1):
        a = w[i]
        b = w[i-1]
        g_val, x, y = exgcd(a, m)
        assert b % g_val == 0, "No solution"
        x0 = (x * (b // g_val)) % (m // g_val)
        sequence.append(x0)
    
    current = 1
    prefix_products = []
    for num in sequence:
        current = (current * num) % m
        prefix_products.append(current)
    
    return len(sequence), prefix_products

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CvulnerablekerbalsVerificationTool(BaseTool):
    """Cvulnerablekerbals验证工具"""
    
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
            score = CvulnerablekerbalsRewardCalculator.verify_score(
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
            logger.error(f"CvulnerablekerbalsVerificationTool执行错误: {str(e)}")
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

