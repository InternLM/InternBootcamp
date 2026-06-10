import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CayoubsfunctionRewardCalculator(BaseRewardCalculator):
    """Cayoubsfunction奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用非贪婪匹配并支持跨行内容
        matches = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output, 
            flags=re.IGNORECASE | re.DOTALL
        )
        if not matches:
            return None
        
        # 提取最后一个答案并清理空白字符
        raw_answer = matches[-1].strip()
        
        # 处理包含逗号分隔的情况
        if ',' in raw_answer:
            raw_answer = raw_answer.replace(',', '')
        
        try:
            return int(raw_answer)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理超大规模数值计算
        n = identity['n']
        m = identity['m']
        
        if m == 0:
            return solution == 0
        
        # 初始化总子串数
        total = n * (n + 1) // 2
        
        if m >= n / 2.0:
            expected = total - (n - m)
            return solution == expected
        
        # 分段计算验证
        c = m + 1
        z = n - m
        base, rem = divmod(z, c)
        
        sum_zeros = (
            rem * (base + 1) * (base + 2) // 2 +
            (c - rem) * base * (base + 1) // 2
        )
        expected = total - sum_zeros
        return solution == expected
    
    # 其他额外方法

