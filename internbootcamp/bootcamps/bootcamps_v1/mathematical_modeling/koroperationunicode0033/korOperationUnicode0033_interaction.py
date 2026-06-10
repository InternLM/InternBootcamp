from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode0033.korOperationUnicode0033_reward_calculator import Koroperationunicode0033RewardCalculator

# 导入依赖库
import math
import re
import random
from typing import Optional




class Koroperationunicode0033Interaction(BaseInteraction):
    """Koroperationunicode0033交互管理器"""
    
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
        score = Koroperationunicode0033RewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode0033问题！"""
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
    def expression_to_str(expr) -> str:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.expression_to_str(expr['left'])
            right = KorOperationUnicode0033bootcamp.expression_to_str(expr['right'])
            return f"({left}{expr['operator']}{right})"
        return str(expr)

    @staticmethod
    def compute_expression(expr) -> float:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.compute_expression(expr['left'])
            right = KorOperationUnicode0033bootcamp.compute_expression(expr['right'])
            if expr['operator'] == '①':
                return math.sqrt(left) + right**2
            return math.sqrt(left) * right
        return float(expr)

    @staticmethod
    def parse_solution(solution: str) -> float:
        solution = solution.replace(' ', '')
        # 处理分数
        frac_match = re.match(r'\\frac\{(-?\d+)\}\{(\d+)\}', solution)
        if frac_match:
            return float(frac_match[1]) / float(frac_match[2])

        # 处理根号表达式（支持系数）
        sqrt_match = re.match(r'(-?)(\d*)\\sqrt\{(\d+)\}', solution)
        if sqrt_match:
            sign = -1 if sqrt_match[1] else 1
            coeff = float(sqrt_match[2] or 1) * sign
            return coeff * math.sqrt(float(sqrt_match[3]))

        # 处理纯根号
        if solution.startswith('\\sqrt'):
            return math.sqrt(float(re.search(r'\d+', solution).group()))

        return float(solution)
