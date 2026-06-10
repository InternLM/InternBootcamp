from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25ce.korOperationUnicode25ce_reward_calculator import Koroperationunicode25ceRewardCalculator

# 导入依赖库
import random
import re




class Koroperationunicode25ceInteraction(BaseInteraction):
    """Koroperationunicode25ce交互管理器"""
    
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
        score = Koroperationunicode25ceRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode25ce问题！"""
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
    def compute_operator(a, b):
        """计算a◎b对应的复数平方"""
        return (a**2 - b**2, 2*a*b)

    def _generate_equation_case(self):
        """生成包含多种形式的方程"""
        equation_type = random.choice([
            'basic_left', 
            'basic_right',
            'scalar_left',
            'scalar_right'
        ])

        X = random.randint(self.min_val, self.max_val)
        a = random.randint(1, 5)  # 避免a为0导致多解
        b = random.randint(self.min_val, self.max_val)
        c = random.randint(self.min_val, self.max_val)
        k = random.randint(2, 5)

        if equation_type.startswith('basic'):
            term1_real, term1_imag = self.compute_operator(X, a)
            term2_real, term2_imag = self.compute_operator(b, c)
            op = '+' if random.random() < 0.5 else '-'

            if equation_type == 'basic_left':
                # (X◎a) ± (b◎c) = target
                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'left',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }
            else:  # basic_right
                # (b◎c) ± (X◎a) = target
                target_real = term2_real + term1_real if op == '+' else term2_real - term1_real
                target_imag = term2_imag + term1_imag if op == '+' else term2_imag - term1_imag
                return {
                    'type': 'equation',
                    'form': f'({b}◎{c}) {op} (X◎{a})',
                    'x_pos': 'right',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }

        else:  # scalar类型
            scalar = k
            if equation_type == 'scalar_left':
                # (X◎a) ± k×(b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term2_real, term2_imag = self.compute_operator(b, c)
                term2_real *= scalar
                term2_imag *= scalar
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} {scalar}×({b}◎{c})',
                    'x_pos': 'left_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }
            else:  # scalar_right
                # k×(X◎a) ± (b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term1_real *= scalar
                term1_imag *= scalar
                term2_real, term2_imag = self.compute_operator(b, c)
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'{scalar}×(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'right_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }

    @staticmethod
    def parse_complex(s):
        s = s.replace(' ', '').lower().replace('i', 'j').rstrip('j')
        try:
            c = complex(s)
            return (int(c.real), int(c.imag))
        except:
            if s:
                return (int(s), 0)
            return (0, 0)
