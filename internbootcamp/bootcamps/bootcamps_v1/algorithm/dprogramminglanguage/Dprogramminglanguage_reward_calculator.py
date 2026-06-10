import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re




class DprogramminglanguageRewardCalculator(BaseRewardCalculator):
    """Dprogramminglanguage奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = [line.strip() for line in last_match.split('\n') if line.strip()]
        solution = []
        for line in lines:
            try:
                solution.append(int(line))
            except ValueError:
                continue
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = []
        variables = identity['variables']
        for call in identity['calls']:
            call_name = call['name']
            var_names = call['vars']
            if not var_names:
                expected.append(0)
                continue
            var_types = [variables[name] for name in var_names]
            count = 0
            for proc in identity['procedures']:
                if proc['name'] != call_name:
                    continue
                if len(proc['params']) != len(var_names):
                    continue
                match = True
                for p_type, v_type in zip(proc['params'], var_types):
                    if p_type != 'T' and p_type != v_type:
                        match = False
                        break
                if match:
                    count += 1
            expected.append(count)
        return solution == expected
    
    # 其他额外方法

