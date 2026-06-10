from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cjzzhuandapples.Cjzzhuandapples_reward_calculator import CjzzhuandapplesRewardCalculator

# 导入依赖库
import math
import random




class CjzzhuandapplesInteraction(BaseInteraction):
    """Cjzzhuandapples交互管理器"""
    
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
        score = CjzzhuandapplesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cjzzhuandapples问题！"""
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
    @staticmethod
    def compute_max_groups(n):
        if n < 2:
            return 0
        used = [False] * (n + 1)
        primes = []

        # Efficient sieve to find primes up to n//2
        sieve_size = (n // 2) + 1
        sieve = [True] * sieve_size
        sieve[0] = sieve[1] = False
        for i in range(2, int(math.isqrt(sieve_size)) + 1):
            if sieve[i]:
                sieve[i*i::i] = [False] * len(sieve[i*i::i])

        # Collect primes in the order: odd primes first, then 2
        primes = [i for i in range(3, sieve_size, 2) if sieve[i]]
        if 2 <= sieve_size:
            primes.append(2)

        total_groups = 0
        for prime in primes:
            if prime > n // 2:
                continue

            # Collect multiples of prime
            multiples = []
            if not used[prime]:
                multiples.append(prime)
                used[prime] = True

            max_multiple = n // prime
            for multiplier in range(3, max_multiple + 1):
                num = prime * multiplier
                if not used[num]:
                    multiples.append(num)
                    used[num] = True

            # Handle odd count
            if len(multiples) % 2 != 0:
                candidate = prime * 2
                if candidate <= n and not used[candidate]:
                    multiples.append(candidate)
                    used[candidate] = True

            total_groups += len(multiples) // 2

        return total_groups
