from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.cryptography.koroperationunicode2295.korOperationUnicode2295_reward_calculator import Koroperationunicode2295RewardCalculator

# 导入依赖库
import re
import random




class Koroperationunicode2295Interaction(BaseInteraction):
    """Koroperationunicode2295交互管理器"""
    
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
        score = Koroperationunicode2295RewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode2295问题！"""
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
    def _generate_equation_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        for _ in range(100):
            x = random.uniform(-self.max_operand, self.max_operand)
            x = round(x, 1)  # 允许一位小数
            operand_index = random.choice([0, 1])
            part = random.choice(['a', 'b'])

            left_a = random.randint(-self.max_operand, self.max_operand)
            left_b = random.randint(-self.max_operand, self.max_operand)
            right_a = random.randint(-self.max_operand, self.max_operand)
            right_b = random.randint(-self.max_operand, self.max_operand)
            operator = random.choice(operators)

            if operand_index == 0:
                left_operand = {'a': 'X' if part == 'a' else left_a, 'b': 'X' if part == 'b' else left_b}
                right_operand = {'a': right_a, 'b': right_b}
                a1 = x if part == 'a' else left_a
                b1 = x if part == 'b' else left_b
                a2, b2 = right_a, right_b
            else:
                left_operand = {'a': left_a, 'b': left_b}
                right_operand = {'a': 'X' if part == 'a' else right_a, 'b': 'X' if part == 'b' else right_b}
                a1, b1 = left_a, left_b
                a2 = x if part == 'a' else right_a
                b2 = x if part == 'b' else right_b

            # 处理分母有效性
            if operator == '/':
                if (a2 == 0 and b2 == 0):
                    continue
                denominator = a2**2 + b2**2
                if denominator == 0:
                    continue

            try:
                if operator == '+':
                    target_real = a1 + a2
                    target_imag = b1 + b2
                elif operator == '-':
                    target_real = a1 - a2
                    target_imag = b1 - b2
                elif operator == '*':
                    target_real = a1 * a2 - b1 * b2
                    target_imag = a1 * b2 + b1 * a2
                else:
                    denominator = a2**2 + b2**2
                    target_real = (a1 * a2 + b1 * b2) / denominator
                    target_imag = (b1 * a2 - a1 * b2) / denominator

                # 允许浮点结果，保留两位小数
                target_real = round(target_real, 2)
                target_imag = round(target_imag, 2)

                return {
                    'type': 'equation',
                    'left_operands': [left_operand, right_operand],
                    'operator': operator,
                    'target_real': target_real,
                    'target_imag': target_imag,
                    'unknown': {'operand_index': operand_index, 'part': part},
                    'solution': round(x, 2)
                }
            except:
                continue
        return self._generate_compute_case()

    def _generate_compute_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        operator = random.choice(operators)

        for _ in range(100):
            a = random.randint(-self.max_operand, self.max_operand)
            b = random.randint(-self.max_operand, self.max_operand)
            c = random.randint(-self.max_operand, self.max_operand)
            d = random.randint(-self.max_operand, self.max_operand)

            if operator == '/' and (c == 0 and d == 0):
                continue

            if operator == '+':
                real = a + c
                imag = b + d
            elif operator == '-':
                real = a - c
                imag = b - d
            elif operator == '*':
                real = a * c - b * d
                imag = a * d + b * c
            else:
                denominator = c**2 + d**2
                real = (a * c + b * d) / denominator
                imag = (b * c - a * d) / denominator

            # 保留两位小数
            real = round(real, 2)
            imag = round(imag, 2)

            return {
                'type': 'compute',
                'operator': operator,
                'left_a': a,
                'left_b': b,
                'right_a': c,
                'right_b': d,
                'solution_real': real,
                'solution_imag': imag
            }

        return {
            'type': 'compute',
            'operator': '+',
            'left_a': random.randint(-self.max_operand, self.max_operand),
            'left_b': random.randint(-self.max_operand, self.max_operand),
            'right_a': random.randint(-self.max_operand, self.max_operand),
            'right_b': random.randint(-self.max_operand, self.max_operand),
            'solution_real': 0,
            'solution_imag': 0
        }
