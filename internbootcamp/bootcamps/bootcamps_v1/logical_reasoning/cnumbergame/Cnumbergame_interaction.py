from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cnumbergame.Cnumbergame_reward_calculator import CnumbergameRewardCalculator

# 导入依赖库
import re
import math
import random




class CnumbergameInteraction(BaseInteraction):
    """Cnumbergame交互管理器"""
    
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
        score = CnumbergameRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnumbergame问题！"""
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
    def _generate_odd_prime(self, min_p=3, max_p=None):
        max_p = max_p or self.max_n // 2
        if min_p % 2 == 0:
            min_p += 1
        attempts = 0
        while attempts < 1000:
            p = random.randint(min_p, max_p)
            if p % 2 == 0:
                continue
            if self.is_prime(p):
                return p
            attempts += 1
        return 3  # fallback

    def _generate_odd_composite(self, min_val=9, max_val=None):
        max_val = max_val or self.max_n // 2
        while True:
            num = random.randint(min_val, max_val)
            if num % 2 == 0:
                continue
            if not self.is_prime(num):
                return num

    @staticmethod
    def is_prime(num):
        if num < 2:
            return False
        if num % 2 == 0:
            return num == 2
        for i in range(3, int(math.isqrt(num)) + 1, 2):
            if num % i == 0:
                return False
        return True

    @staticmethod
    def get_correct_answer(n):
        original_n = n
        t = 0
        while n % 2 == 0:
            n = n // 2
            t += 1
        k = n

        if t == 0:
            return "FastestFinger" if k == 1 else "Ashishgup"
        elif t == 1:
            if k == 1:
                return "Ashishgup"
            is_prime = Cnumbergamebootcamp.is_prime(k)
            return "FastestFinger" if is_prime else "Ashishgup"
        else:
            return "FastestFinger" if k == 1 else "Ashishgup"
