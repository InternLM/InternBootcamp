import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque




class CcandiesdistributionRewardCalculator(BaseRewardCalculator):
    """Ccandiesdistribution奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        from itertools import dropwhile
        
        # 清理特殊字符
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', output)  # 移除ANSI转义码
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', clean_output, re.DOTALL)
        
        if not matches:
            return None
        
        content = matches[-1].strip()
        lines = list(filter(None, map(str.strip, content.splitlines())))
        
        if not lines:
            return None
        
        status = lines[0].upper()
        if status not in ('YES', 'NO'):
            return None
        
        result = {'status': status}
        if status == 'YES' and len(lines) >= 2:
            try:
                result['a'] = list(map(int, re.findall(r'\d+', lines[1])))
            except ValueError:
                return None
        
        return result
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        expected_solvable = identity['solvable']
        
        # 验证否定结论
        if solution['status'] == 'NO':
            return not expected_solvable
        
        # 验证肯定结论
        if solution.get('status') != 'YES' or 'a' not in solution:
            return False
        
        a = solution['a']
        n = identity['n']
        l = identity['l']
        r = identity['r']
        
        # 基础校验
        if len(a) != n or any(not 1 <= x <= n for x in a):
            return False
        
        # 精确验证
        try:
            for i in range(n):
                actual_l = sum(a[j] > a[i] for j in range(i))
                actual_r = sum(a[j] > a[i] for j in range(i+1, n))
                
                if actual_l != l[i] or actual_r != r[i]:
                    return False
        except IndexError:
            return False
        
        return True
    
    # 其他额外方法

