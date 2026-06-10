import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CgivenlengthandsumofdigitsRewardCalculator(BaseRewardCalculator):
    """Cgivenlengthandsumofdigits奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """鲁棒的答案提取机制"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL|re.IGNORECASE)
        return matches[-1].replace(' ', '').strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """三维验证体系：格式检查、数学验证、边界条件"""
        try:
            m, s = identity['m'], identity['s']
            
            # Case 1: 验证-1 -1的特殊情况
            if solution == "-1-1":
                return not cls._has_valid_solution(m, s)
            
            # Case 2: 格式验证
            if len(solution) != 2*m + 1 or solution[m] != ' ':
                return False
            min_num, max_num = solution[:m], solution[m+1:]
            
            # 前导零检查
            if (m > 1 and (min_num[0] == '0' or max_num[0] == '0')):
                return False
            
            # 数值验证
            return (sum(map(int, min_num)) == s and
                    sum(map(int, max_num)) == s and
                    cls._has_valid_solution(m, s))
        except:
            return False
    
    # 其他额外方法

