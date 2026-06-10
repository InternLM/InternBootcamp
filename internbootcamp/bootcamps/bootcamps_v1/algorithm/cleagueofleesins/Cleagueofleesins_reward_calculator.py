import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re




class CleagueofleesinsRewardCalculator(BaseRewardCalculator):
    """Cleagueofleesins奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        patterns = [
            r'\[answer\]([\d\s]+?)\[/answer\]',  # 严格匹配数字和空格
            r'(?:\n|^)(\d+(?:\s+\d+)+)(?:\n|$)'  # 匹配纯数字序列
        ]
        for pattern in patterns:
            matches = re.findall(pattern, output)
            if matches:
                last_match = matches[-1].strip()
                try:
                    return list(map(int, last_match.split()))
                except:
                    continue
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证基础参数
        n = identity['n']
        if not solution or len(solution) != n:
            return False
        if set(solution) != set(range(1, n+1)):
            return False
        
        # 构建有效三元组集合
        expected = defaultdict(int)
        for t in identity['triples']:
            key = tuple(sorted(t))
            expected[key] += 1
        
        # 验证解的三元组
        actual = defaultdict(int)
        for i in range(len(solution)-2):
            triplet = tuple(sorted(solution[i:i+3]))
            actual[triplet] += 1
        
        # 比较多重集合
        return actual == expected
    
    # 其他额外方法

