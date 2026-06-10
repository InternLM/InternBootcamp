from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bsashaandonemorename.Bsashaandonemorename_reward_calculator import BsashaandonemorenameRewardCalculator

# 导入依赖库
import random
import string
import re




class BsashaandonemorenameInteraction(BaseInteraction):
    """Bsashaandonemorename交互管理器"""
    
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
        score = BsashaandonemorenameRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bsashaandonemorename问题！"""
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
    def _generate_impossible_case(self):
        n = random.randint(self.min_length, self.max_length)
        c = random.choice(string.ascii_lowercase)
        return c * n

    def _generate_k1_case(self):
        while True:
            base = ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, self.max_length//2)))
            if base != base[::-1]:
                s = base + base[::-1]
                if s != s[::-1]:
                    continue
                return s

    def _generate_k2_case(self):
        while True:
            s = self._generate_complex_palindrome()
            if all(c == s[0] for c in s):
                continue
            return s

    def _generate_complex_palindrome(self):
        """生成无法通过简单旋转得到不同解的复杂回文"""
        while True:
            left = []
            for _ in range(random.randint(2, self.max_length//2)):
                candidates = [c for c in string.ascii_lowercase if not left or c != left[-1]]
                left.append(random.choice(candidates))
            left_str = ''.join(left)
            right_str = left_str[::-1]

            if random.choice([True, False]) and len(left_str) > 1:
                mid = random.choice(string.ascii_lowercase.replace(left_str[-1], ''))
            else:
                mid = ''
            s = left_str + mid + right_str

            if not any(self._is_valid_rotation(s, i) for i in range(1, len(s))):
                return s

    @staticmethod
    def _is_valid_rotation(s, i):
        rotated = s[i:] + s[:i]
        return rotated != s and rotated == rotated[::-1]
