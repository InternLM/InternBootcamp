from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmagicfive.Cmagicfive_reward_calculator import CmagicfiveRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CmagicfiveInteraction(BaseInteraction):
    """Cmagicfive交互管理器"""
    
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
        score = CmagicfiveRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmagicfive问题！"""
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
    def _gen_has_05(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        chars = []
        for _ in range(length):
            if random.random() < 0.3:
                chars.append(random.choice(['0', '5']))
            else:
                chars.append(random.choice('12346789'))
        if not any(c in {'0','5'} for c in chars):
            chars[random.randint(0, len(chars)-1)] = random.choice(['0','5'])
        return ''.join(chars)

    def _gen_random(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def compute_ways(a, k):
        MOD = 10**9 + 7
        if not a:
            return 0

        l = len(a)
        two_l = pow(2, l, MOD)
        denominator = (two_l - 1) % MOD
        inv_denominator = pow(denominator, MOD-2, MOD) if denominator != 0 else 0

        power_sum = pow(two_l, k, MOD)

        base_sum = 0
        pwr = 1  # 对应2^0
        for char in a:
            if char in {'0', '5'}:
                base_sum = (base_sum + pwr) % MOD
            pwr = (pwr * 2) % MOD

        if inv_denominator == 0:
            total = 0
        else:
            numerator = (base_sum * (power_sum - 1 + MOD)) % MOD
            total = (numerator * inv_denominator) % MOD
        return total
