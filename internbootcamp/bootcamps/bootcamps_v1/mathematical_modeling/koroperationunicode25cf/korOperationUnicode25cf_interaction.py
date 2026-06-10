from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25cf.korOperationUnicode25cf_reward_calculator import Koroperationunicode25cfRewardCalculator

# 导入依赖库
import random
import re
import sympy as sp
from sympy.abc import x
from sympy.abc import a
from sympy.abc import b




class Koroperationunicode25cfInteraction(BaseInteraction):
    """Koroperationunicode25cf交互管理器"""
    
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
        score = Koroperationunicode25cfRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korOperationUnicode25cf问题！"""
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
        func_info = self._generate_random_function()
        f_expr, f_str = func_info['expr'], func_info['str']

        if func_info['str'] == '1/x':
            a_val, b_val = self._generate_valid_interval_for_reciprocal()
        else:
            a_val, b_val = self._generate_valid_interval()

        integral = sp.integrate(f_expr, (x, a_val, b_val))
        result = self._safe_eval(integral + 6)

        return {
            'problem_type': 'compute',
            'f': f_str,
            'a': a_val,
            'b': b_val,
            'operator': random.choice(self.operator_symbols),
            'correct_answer': result
        }

    def _generate_solve_case(self):
        func_info = self._generate_random_function(solve_case=True)
        f_expr, f_str = func_info['expr'], func_info['str']
        target_var = random.choice(['a', 'b'])
        known_var = 'b' if target_var == 'a' else 'a'

        # Handle special case for 1/x
        if f_str == '1/x':
            sign_constraint = 'positive'
        else:
            sign_constraint = None

        if target_var == 'a':
            b_val = self._generate_value(exclude_zero=f_str == '1/x', sign=sign_constraint)
            a_sample = self._generate_value(exclude=b_val, sign=sign_constraint)
        else:
            a_val = self._generate_value(exclude_zero=f_str == '1/x', sign=sign_constraint)
            b_sample = self._generate_value(exclude=a_val, sign=sign_constraint)

        # Generate equation with explicit result value
        simple_case = func_info.get('simple', False)
        result_val = random.randint(5, 15) if simple_case else random.randint(3, 20)

        if target_var == 'a':
            integral = sp.integrate(f_expr, (x, sp.Symbol('a'), b_val))
        else:
            integral = sp.integrate(f_expr, (x, a_val, sp.Symbol('b')))

        equation = integral + 6 - result_val

        solutions = self._solve_equation(equation, target_var)
        if not solutions:
            return self.case_generator()

        return {
            'problem_type': 'solve',
            'f': f_str,
            'known_var': known_var,
            'known_value': b_val if target_var == 'a' else a_val,
            'target_var': target_var,
            'operator': random.choice(self.operator_symbols),
            'result': result_val,  # Add result field
            'correct_answers': solutions
        }

    def _generate_random_function(self, solve_case=False):
        func_type = random.choice(self.function_list)
        params = {}

        if func_type == 'm*x':
            params['m'] = random.choice([-2, -1, 1, 2, 3])
            return {'expr': params['m']*x, 'str': f"{params['m']}x", 'simple': True}
        elif func_type == 'x**n':
            params['n'] = random.randint(2, 3) if solve_case else random.randint(2, 4)
            return {'expr': x**params['n'], 'str': f"x^{params['n']}"}
        elif func_type == '1/x':
            return {'expr': 1/x, 'str': "1/x"}
        elif func_type in ('sin(x)', 'cos(x)'):
            return {'expr': sp.__dict__[func_type[:3]](x), 'str': func_type}
        raise ValueError("Invalid function type")

    def _generate_valid_interval(self):
        while True:
            a_val = random.randint(*self.default_a_range)
            b_val = random.randint(*self.default_b_range)
            if a_val != b_val:
                return (a_val, b_val) if a_val < b_val else (b_val, a_val)

    def _generate_valid_interval_for_reciprocal(self):
        while True:
            # Ensure same sign and non-zero
            if random.choice([True, False]):
                a_val = random.randint(1, self.default_a_range[1])
                b_val = random.randint(1, self.default_b_range[1])
            else:
                a_val = random.randint(self.default_a_range[0], -1)
                b_val = random.randint(self.default_b_range[0], -1)
            if a_val != b_val:
                return (a_val, b_val) if a_val < b_val else (b_val, a_val)

    def _generate_value(self, exclude=None, exclude_zero=False, sign=None):
        while True:
            val = random.randint(*self.default_a_range)
            if sign == 'positive' and val <= 0:
                continue
            if sign == 'negative' and val >= 0:
                continue
            if exclude_zero and val == 0:
                continue
            if val == exclude:
                continue
            return val

    def _solve_equation(self, equation, target_var):
        symbol = sp.Symbol(target_var)
        try:
            solutions = sp.solve(equation, symbol)
            real_solutions = [sol.evalf() for sol in solutions if sol.is_real]
            return list({round(float(sol), 6) for sol in real_solutions if sol.is_real})
        except:
            return []

    @staticmethod
    def _safe_eval(expr):
        try:
            return float(expr.evalf())
        except:
            return float(expr)
