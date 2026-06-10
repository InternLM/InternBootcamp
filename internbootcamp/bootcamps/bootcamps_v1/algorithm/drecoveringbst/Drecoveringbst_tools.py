import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drecoveringbst.Drecoveringbst_reward_calculator import DrecoveringbstRewardCalculator

# 导入依赖库
import re
import math
import random
from math import gcd
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DrecoveringbstVerificationTool(BaseTool):
    """Drecoveringbst验证工具"""
    
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
            score = DrecoveringbstRewardCalculator.verify_score(
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
            logger.error(f"DrecoveringbstVerificationTool执行错误: {str(e)}")
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
    def _sieve(self, n):
        sieve = [True] * (n+1)
        sieve[0:2] = [False]*2
        for i in range(2, int(n**0.5)+1):
            if sieve[i]:
                sieve[i*i::i] = [False]*len(sieve[i*i::i])
        return [i for i, b in enumerate(sieve) if b]

    def _generate_yes_case(self):
        """生成保证有解的案例：通过链式结构构造"""
        # 方法一：构建链式树（完全左/右子树）
        n = random.randint(self.n_min, self.n_max)
        base = random.choice([2, 3, 4, 5, 6])
        step = random.choice([2, 3, 4])
        arr = sorted([base * (step**i) for i in range(n)])

        # 方法二：共享因子的随机组合
        factors = random.sample(self.prime_pool, 3)
        candidates = []
        for _ in range(2*n):
            p = random.choice(factors)
            q = random.choice(factors)
            if p != q:
                candidates.append(p*q)
        arr = sorted(list(set(candidates)))[:n]
        if len(arr) < self.n_min:
            return None

        expected = self.check_possible(arr)
        if expected == 'Yes':
            return {
                'n': len(arr),
                'array': arr,
                'expected_answer': expected
            }
        return None

    def _generate_no_case(self):
        """生成保证无解的案例：互质数或特殊结构"""
        # 方法一：使用互质数
        primes = random.sample(self.prime_pool, self.n_max*2)
        arr = sorted(primes[:random.randint(self.n_min, self.n_max)])
        if all(math.gcd(a,b)==1 for a in arr for b in arr if a!=b):
            return {
                'n': len(arr),
                'array': arr,
                'expected_answer': 'No'
            }

        # 方法二：构造无法形成BST结构的案例
        while True:
            base = random.choice([2,3])
            arr = sorted([base**i for i in range(1, self.n_max+1)])
            if self.check_possible(arr) == 'No':
                return {
                    'n': len(arr),
                    'array': arr,
                    'expected_answer': 'No'
                }
            break

        return None

    @staticmethod
    def check_possible(a):
        # 优化后的验证算法（带记忆化）
        n = len(a)
        gcd_cache = [[math.gcd(a[i], a[j]) > 1 for j in range(n)] for i in range(n)]
        parent = [[-1]*n for _ in range(n)]
        dp = [[False]*n for _ in range(n)]

        # 构建根节点可能性
        for i in range(n):
            dp[i][i] = True

        # 区间DP
        for l in range(2, n+1):
            for i in range(n - l + 1):
                j = i + l - 1
                for k in range(i, j+1):
                    left_ok = (k == i) or (dp[i][k-1] and gcd_cache[k][k-1])
                    right_ok = (k == j) or (dp[k+1][j] and gcd_cache[k][k+1])
                    if left_ok and right_ok:
                        dp[i][j] = True
                        parent[i][j] = k
                        break

        return 'Yes' if dp[0][n-1] else 'No'
