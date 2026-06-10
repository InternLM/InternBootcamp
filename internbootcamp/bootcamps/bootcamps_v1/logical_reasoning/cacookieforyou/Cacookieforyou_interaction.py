from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cacookieforyou.Cacookieforyou_reward_calculator import CacookieforyouRewardCalculator

# 导入依赖库
import re
import random




class CacookieforyouInteraction(BaseInteraction):
    """Cacookieforyou交互管理器"""
    
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
        score = CacookieforyouRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cacookieforyou问题！"""
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
    def _generate_zero_cookie_case(self):
        """确保至少有一个客人存在"""
        a, b = 0, 0
        while True:
            n = random.randint(0, self.max_value)
            m = random.randint(0, self.max_value)
            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}

    def _generate_single_type_guest_case(self):
        """确保至少有一类客人存在"""
        while True:
            if random.random() < 0.5:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': random.randint(0, self.max_value),
                    'm': 0
                }
            else:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': 0,
                    'm': random.randint(0, self.max_value)
                }
            if case['n'] + case['m'] > 0:
                return case

    def _generate_yes_case(self):
        """添加重试机制防止死循环"""
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            if a + b == 0:
                continue

            a_new, b_new = max(a, b), min(a, b)
            max_m = b_new
            m = random.randint(0, max_m)
            remaining = (a_new + b_new) - m
            n = random.randint(0, remaining)

            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        # 保底生成合法案例
        return {'a': 2, 'b': 1, 'n': 1, 'm': 1}

    def _generate_no_case(self):
        strategies = [
            self._generate_case_total_exceed,
            self._generate_case_m_exceed,
            self._generate_zero_cookie_angry_case
        ]
        return random.choice(strategies)()

    def _generate_case_total_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(1, self.max_value)
            b = random.randint(1, self.max_value)
            total = a + b
            min_guest = total + 1
            n = random.randint(0, min_guest)
            m = min_guest - n
            if m < 0:
                m = 0
                n = min_guest
            if a + b < n + m:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 1, 'b': 1, 'n': 2, 'm': 1}

    def _generate_case_m_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            a_new, b_new = max(a, b), min(a, b)
            if b_new == 0:
                continue
            m = random.randint(b_new + 1, self.max_value)
            remaining = (a_new + b_new) - m
            n = random.randint(0, max(remaining, 0))
            if (n + m) <= (a_new + b_new):
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 3, 'b': 1, 'n': 1, 'm': 3}

    def _generate_zero_cookie_angry_case(self):
        return {'a': 0, 'b': 0, 
                'n': random.randint(1, self.max_value),
                'm': random.randint(0, self.max_value)}
