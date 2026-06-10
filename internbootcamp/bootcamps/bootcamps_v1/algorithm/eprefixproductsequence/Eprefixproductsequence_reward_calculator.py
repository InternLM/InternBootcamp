import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class EprefixproductsequenceRewardCalculator(BaseRewardCalculator):
    """Eprefixproductsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强正则表达式鲁棒性，允许换行和空格"""
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        # 清理首尾空白行
        return '\n'.join(line.strip() for line in last_match.splitlines() if line.strip())
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """添加模运算结果的严格验证"""
        n = identity['n']
        possible = identity['possible']
        lines = solution.strip().split('\n')
        if not lines:
            return False
        
        # 验证YES/NO与possible的一致性
        first_line = lines[0].strip().upper()
        if first_line == 'YES' and not possible:
            return False
        if first_line == 'NO' and possible:
            return False
        
        # 处理NO情况
        if first_line == 'NO':
            return len(lines) == 1
        
        # 处理YES情况
        if len(lines) != n + 1:
            return False  # 行数不匹配
        
        try:
            sequence = list(map(int, lines[1:n+1]))
        except ValueError:
            return False
        
        # 验证元素为1~n的排列
        if sorted(sequence) != list(range(1, n+1)):
            return False
        
        # 验证前缀积模运算结果
        prefix_mod = []
        current = 1
        for num in sequence:
            current = (current * num) % n
            prefix_mod.append(current)
        return sorted(prefix_mod) == list(range(n))
    
    # 其他额外方法

