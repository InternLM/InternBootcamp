from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drecoveringbst.Drecoveringbst_reward_calculator import DrecoveringbstRewardCalculator

# 导入依赖库
import re
import math
import random
from math import gcd
from collections import defaultdict




class DrecoveringbstInteraction(BaseInteraction):
    """Drecoveringbst交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = DrecoveringbstRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Drecoveringbst问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
