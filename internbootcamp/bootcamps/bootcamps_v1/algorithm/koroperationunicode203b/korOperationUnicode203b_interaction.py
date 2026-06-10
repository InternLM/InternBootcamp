from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.koroperationunicode203b.korOperationUnicode203b_reward_calculator import Koroperationunicode203bRewardCalculator

# 导入依赖库
import json
import random
import re




class Koroperationunicode203bInteraction(BaseInteraction):
    """Koroperationunicode203b交互管理器"""
    
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
        score = Koroperationunicode203bRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode203b问题！"""
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
    def _generate_compute_case(self):
        for _ in range(self.max_attempts):
            num_operands = random.choices([2,3,4], weights=[5,3,1])[0]
            operands = [random.randint(1, self.max_operand) for _ in range(num_operands)]

            try:
                current_value = operands[0]
                for op in operands[1:]:
                    current_value = self._compute_operation(current_value, op, self.C)
            except ZeroDivisionError:
                continue

            # 允许有限概率生成结果为24的题目
            if current_value !=24 or random.random() < 0.2:
                return {
                    'type': 'compute',
                    'expression': operands,
                    'C': self.C,
                    'answer': int(current_value)
                }

        # 保底返回简单计算题
        return {
            'type': 'compute',
            'expression': [4,7],
            'C': self.C,
            'answer': 24
        }

    def _compute_operation(self, a, b, C):
        if b == 0 or a == 0:
            return 24
        if a % b == 0:
            return (a // b) + C
        if b % a == 0:
            return (b // a) + C
        return 24

    def _generate_solve_x_case(self):
        for _ in range(self.max_attempts):
            # 随机选择生成方向
            if random.random() < 0.5:  # 生成 a※X=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                # 寻找所有可能的X解
                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(a, X, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"{a}※X={target}",
                        'solutions': solutions,
                        'C': self.C
                    }
            else:  # 生成 X※a=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(X, a, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"X※{a}={target}",
                        'solutions': solutions,
                        'C': self.C
                    }

        # 保底返回单解问题
        return {
            'type': 'solve_x',
            'equation': "X※4=6",
            'solutions': [8],  # 8※4=2+2=4?
            'C': self.C
        }

    def _generate_solve_c_case(self):
        for _ in range(self.max_attempts):
            # 随机生成方向
            if random.random() < 0.5:
                a = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                b = a * factor
                expected = factor + self.C  # a※b = b/a + C
            else:
                b = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                a = b * factor
                expected = factor + self.C  # a※b = a/b + C

            # 避免除零错误
            if a == 0 or b == 0:
                continue

            return {
                'type': 'solve_c',
                'equation': f"{a}※{b}={expected}",
                'answer': self.C
            }

        # 保底返回
        return {
            'type': 'solve_c',
            'equation': "25※5=8",
            'answer': 3  # 25/5=5 +3=8
        }
