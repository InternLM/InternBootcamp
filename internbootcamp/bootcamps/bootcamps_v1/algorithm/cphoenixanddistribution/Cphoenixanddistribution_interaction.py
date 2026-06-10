from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cphoenixanddistribution.Cphoenixanddistribution_reward_calculator import CphoenixanddistributionRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import Counter




class CphoenixanddistributionInteraction(BaseInteraction):
    """Cphoenixanddistribution交互管理器"""
    
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
        score = CphoenixanddistributionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cphoenixanddistribution问题！"""
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
    def _generate_random_case(self):
        n = random.randint(self.min_length, self.max_length)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        k = random.randint(1, max(1, n//2)) if n > 1 else 1
        return {'n': n, 'k': k, 's': s}

    def _generate_edge_case(self):
        case_type = random.choice([1, 2, 3, 4])

        if case_type == 1:  # k=1的特殊情况
            s = ''.join(sorted(random.choices(string.ascii_lowercase, k=random.randint(5, 10))))
            return {'n': len(s), 'k': 1, 's': s}

        elif case_type == 2:  # 所有字符相同的情况
            char = random.choice(string.ascii_lowercase)
            n = random.randint(5, 15)
            k = random.randint(1, n)
            return {'n': n, 'k': k, 's': char * n}

        elif case_type == 3:  # 需要均匀分配的情况
            base_char = random.choice(string.ascii_lowercase)
            other_char = chr(ord(base_char) + 1)
            s = base_char * 5 + other_char * 10
            k = random.randint(3, 5)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

        else:  # 首字符不满足k需求的情况
            first_char = 'a'
            rest_chars = ''.join(random.choices(string.ascii_lowercase[1:], k=random.randint(8, 15)))
            s = first_char * 3 + rest_chars
            k = 5  # 大于首字符数量(3)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

    @classmethod
    def compute_correct_answer(cls, s, k):
        sorted_s = ''.join(sorted(s))
        n = len(sorted_s)
        first_char_count = sorted_s.count(sorted_s[0])

        if first_char_count < k or n == k:
            return sorted_s[k-1]
        else:
            if sorted_s[k] != sorted_s[-1]:
                return sorted_s[0] + sorted_s[k:]
            else:
                repeat = (n - 1) // k
                return sorted_s[0] + sorted_s[-1] * repeat

    @staticmethod
    def split_into_parts(sorted_s, k):
        # 辅助方法用于验证分割逻辑
        parts = []
        if Counter(sorted_s) == Counter(sorted_s[0]*len(sorted_s)):
            base = sorted_s[0]
            per_part = len(sorted_s) // k
            remainder = len(sorted_s) % k
            for i in range(k):
                parts.append(base * (per_part + (1 if i < remainder else 0)))
        else:
            parts = [sorted_s[0]] * k
            remaining = sorted_s[k:]
            for i in range(len(remaining)):
                parts[i % k] += remaining[i]
            parts = [''.join(sorted(p)) for p in parts]
        return parts
