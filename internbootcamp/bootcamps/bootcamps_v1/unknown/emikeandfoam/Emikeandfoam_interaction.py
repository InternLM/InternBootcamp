from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.unknown.emikeandfoam.Emikeandfoam_reward_calculator import EmikeandfoamRewardCalculator

# 导入依赖库
import math
import random
from collections import defaultdict




class EmikeandfoamInteraction(BaseInteraction):
    """Emikeandfoam交互管理器"""
    
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
        score = EmikeandfoamRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Emikeandfoam问题！"""
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
    @classmethod
    def _compute_expected(cls, n, q, a, queries):
        # 预计算每个数的质因数分解
        prime_factors_list = []
        max_ai = max(a) if a else 1
        sieve = cls._build_sieve(max_ai)

        for num in a:
            factors = set()
            temp = num
            while temp > 1:
                p = sieve[temp]
                factors.add(p)
                while temp % p == 0:
                    temp //= p
            prime_factors_list.append(sorted(factors))

        # 初始化状态
        in_self = defaultdict(bool)
        divi_counts = defaultdict(int)
        current_total = 0
        answer = 0
        output = []

        for x in queries:
            idx = x-1  # queries是1-based
            num = a[idx]
            factors = prime_factors_list[idx]

            if in_self[idx]:
                # 移除操作
                sign = -1
                in_self[idx] = False
            else:
                # 添加操作
                sign = +1
                in_self[idx] = True

            # 计算当前贡献
            coprime_count = 0
            k = len(factors)
            for mask in range(1, 1 << k):
                d = 1
                bits = 0
                for i in range(k):
                    if mask & (1 << i):
                        d *= factors[i]
                        bits += 1
                cnt = divi_counts[d]
                coprime_count += cnt if bits % 2 else -cnt

            delta = sign * (current_total - coprime_count)
            answer += delta
            output.append(answer)

            # 更新除数计数
            for mask in cls._generate_divisors(num):
                divi_counts[mask] += sign

            current_total += sign

        return output

    @staticmethod
    def _build_sieve(max_num):
        sieve = list(range(max_num+1))
        for i in range(2, int(math.sqrt(max_num))+1):
            if sieve[i] == i:
                for j in range(i*i, max_num+1, i):
                    if sieve[j] == j:
                        sieve[j] = i
        return sieve

    @staticmethod
    def _generate_divisors(num):
        if num == 1:
            return []
        divisors = set()
        for i in range(2, int(math.isqrt(num)) + 1):
            if num % i == 0:
                divisors.update({i, num//i})
        divisors.add(num)
        return divisors
