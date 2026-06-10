import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
import numpy as np
from scipy.integrate import odeint




class LinearodeRewardCalculator(BaseRewardCalculator):
    """Linearode奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            raw_expr = last_match.replace('dx/dt = ', '').strip()
            expr = raw_expr.strip()
            pattern = re.fullmatch(
                r"""
                ([+-]?\s*            # 可选的正负号，后可带空格
                (?:\d+(?:\.\d*)?     # 整数或小数点后数字
                |\.\d+)?             # 或只有小数部分
                (?:[eE][+-]?\d+)?    # 可选的科学计数部分
                )?                   # 整个系数是可选的（允许直接 x 或 -x）
                \s*\*?\s*            # 可选乘号，前后允许空格
                [xX]                 # x 或 X
                """,
                expr,
                re.VERBOSE
            )

            if pattern:
                raw = pattern.group(1)
                if raw is None or raw.strip() == '':
                    return 1.0
                elif raw.strip() in ['+', '+1']:
                    return 1.0
                elif raw.strip() in ['-', '-1']:
                    return -1.0
                else:
                    return float(raw)
            else:
                return None 
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: float, identity: dict) -> bool:
        delta = abs(solution + identity["k"])
        return delta < 1e-2
    
    # 其他额外方法

