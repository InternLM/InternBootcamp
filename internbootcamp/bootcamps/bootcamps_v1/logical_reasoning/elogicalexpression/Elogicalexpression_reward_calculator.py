import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import html




class ElogicalexpressionRewardCalculator(BaseRewardCalculator):
    """Elogicalexpression奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        solution = matches[-1].strip()
        solution = html.unescape(solution)  # 处理HTML转义字符
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        ans = cls._get_ans_list()
        truth_table = identity['truth_table']
        index = int(truth_table, 2)
        if index >= len(ans):
            return False
        expected = html.unescape(ans[index])
        solution = html.unescape(solution)
        return solution == expected
    
    # 其他额外方法

