from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.koroperationunicodeffe1.korOperationUnicodeffe1_reward_calculator import Koroperationunicodeffe1RewardCalculator

# 导入依赖库
import random
import re




class Koroperationunicodeffe1Interaction(BaseInteraction):
    """Koroperationunicodeffe1交互管理器"""
    
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
        score = Koroperationunicodeffe1RewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicodeffe1问题！"""
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
    def generate_finite_case(self):
        element_type = self.element_type
        if element_type == 'mixed':
            element_type = random.choice(['number', 'letter'])

        size_A = random.randint(2, self.max_size)
        size_B = random.randint(2, self.max_size)

        if element_type == 'number':
            elements = list(range(1, 21))
            A = sorted(random.sample(elements, size_A))
            B = sorted(random.sample(elements, size_B))
        else:
            letters = [chr(ord('a') + i) for i in range(26)]
            A = sorted(random.sample(letters, size_A))
            B = sorted(random.sample(letters, size_B))

        A_set = set(A)
        B_set = set(B)
        solution = sorted(list(A_set.symmetric_difference(B_set)))
        return {
            'type': 'finite',
            'A': A,
            'B': B,
            'solution': solution
        }

    def generate_interval_case(self):
        template = random.choice([1, 2, 3])
        if template == 1:  # 非重叠区间
            a = random.randint(-5, 3)
            b = a + random.randint(2, 4)
            while True:
                c = random.randint(b+1, b+3)
                if c > b: break
            A_desc = f'x > {a}'
            B_desc = f'x < {b}'
            solution = f'{{x | x ≤ {a} or x ≥ {b}}}'
        elif template == 2:  # 包含区间
            a = random.randint(2, 5)
            b = random.randint(-3, a-1)
            A_desc = f'x < {a}'
            B_desc = f'x > {b}'
            solution = f'{{x | x ≤ {b} or x ≥ {a}}}'
        else:  # 二次不等式
            c = random.randint(1, 3)
            A_desc = 'x is a real number'
            B_desc = f'x² < {c**2}'
            solution = f'{{x | x ≤ -{c} or x ≥ {c}}}'
        return {
            'type': 'interval',
            'A': A_desc,
            'B': B_desc,
            'solution': solution
        }

    def generate_special_case(self):
        case_type = random.choice([1, 2])
        if case_type == 1:  # 自然数 vs 正整数
            return {
                'type': 'special',
                'A': 'x is a natural number (including 0)',
                'B': 'x is a positive integer',
                'solution': '{0}'
            }
        else:  # 全体实数 vs 空集
            return {
                'type': 'special',
                'A': 'x is a real number',
                'B': 'x is an element of empty set',
                'solution': '{x | x ∈ ℝ}'
            }
