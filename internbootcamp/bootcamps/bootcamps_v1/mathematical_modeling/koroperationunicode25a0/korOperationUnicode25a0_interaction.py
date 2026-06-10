from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25a0.korOperationUnicode25a0_reward_calculator import Koroperationunicode25a0RewardCalculator

# 导入依赖库
import random
import re
import sympy

# === 源文件中的全局变量 ===

x, y = sympy.symbols('x y')


class Koroperationunicode25a0Interaction(BaseInteraction):
    """Koroperationunicode25a0交互管理器"""
    
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
        score = Koroperationunicode25a0RewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode25a0问题！"""
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
    def _generate_term(self):
        term_types = [
            # 多项式项
            lambda: x**random.randint(1, self.max_degree),
            lambda: y**random.randint(1, self.max_degree),
            # 三角函数
            lambda: sympy.sin(random.choice([x, y])),
            lambda: sympy.cos(random.choice([x, y])),
            # 指数函数
            lambda: sympy.exp(x),
            # 分式项
            lambda: sympy.Mul(
                sympy.Poly(random.randint(1, 3)*x**random.randint(0,2), x), 
                sympy.Pow(y, -random.randint(1,2)), 
                evaluate=False
            ),
            # 常数项
            lambda: sympy.Integer(random.randint(1, 5))
        ]
        return random.choice(term_types)()

    def _generate_expression(self):
        num_terms = random.randint(1, self.max_terms)
        expr = sympy.Integer(0)
        for _ in range(num_terms):
            term = self._generate_term()
            # 确保不生成全零表达式
            if expr == 0:
                expr = term
            else:
                expr += term
        return expr
