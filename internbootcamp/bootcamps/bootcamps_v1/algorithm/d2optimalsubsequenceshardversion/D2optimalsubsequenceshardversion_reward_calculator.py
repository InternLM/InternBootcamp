import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class D2optimalsubsequenceshardversionRewardCalculator(BaseRewardCalculator):
    """D2optimalsubsequenceshardversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        answers = []
        for line in matches[-1].strip().split('\n'):
            line = line.strip()
            if re.fullmatch(r'\d+', line):
                answers.append(int(line))
        return answers
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != identity['m']:
            return False
        
        a = identity['a']
        queries = identity['queries']
        n = len(a)
        
        # 构建与参考代码相同的排序逻辑
        sorted_a = sorted([(-val, idx) for idx, val in enumerate(a)])
        
        for sol, (k, pos) in zip(solution, queries):
            if k > n or pos > k or pos < 1:
                return False
            
            # 精确重建选择过程
            selected = sorted(sorted_a[:k], key=lambda x: x[1])
            optimal_subseq = [a[x[1]] for x in selected]
            
            if pos-1 >= len(optimal_subseq) or sol != optimal_subseq[pos-1]:
                return False
        
        return True
    
    # 其他额外方法

