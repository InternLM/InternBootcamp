import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import sympy

# === 源文件中的全局变量 ===

x, y = sympy.symbols('x y')


class Koroperationunicode25a0RewardCalculator(BaseRewardCalculator):
    """Koroperationunicode25a0奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        solution = matches[-1].strip()
        # 清理多余空格和换行
        return re.sub(r'\s+', '', solution)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 转换用户答案
            user_clean = solution.replace('\\', '').replace('{','').replace('}','')
            user_expr = sympy.parse_expr(user_clean, transformations='all')
            
            # 转换标准答案
            ans_expr = sympy.parse_expr(identity['_answer_sympy'])
            
            # 符号等价验证
            diff = sympy.simplify(user_expr - ans_expr)
            return diff.equals(0)
        except Exception as e:
            return False
    
    # 其他额外方法

