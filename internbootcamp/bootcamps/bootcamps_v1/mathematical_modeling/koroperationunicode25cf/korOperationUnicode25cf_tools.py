import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25cf.korOperationUnicode25cf_reward_calculator import Koroperationunicode25cfRewardCalculator

# 导入依赖库
import random
import re
import sympy as sp
from sympy.abc import x
from sympy.abc import a
from sympy.abc import b



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode25cfVerificationTool(BaseTool):
    """Koroperationunicode25cf验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = Koroperationunicode25cfRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"Koroperationunicode25cfVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
