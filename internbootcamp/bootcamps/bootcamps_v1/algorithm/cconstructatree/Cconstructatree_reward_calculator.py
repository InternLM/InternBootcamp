import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re




class CconstructatreeRewardCalculator(BaseRewardCalculator):
    """Cconstructatree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer_block = matches[-1].strip()
        lines = [line.strip() for line in answer_block.split('\n') if line.strip()]
        if not lines:
            return None
        first_line = lines[0].lower()
        if first_line == 'no':
            return 'No'
        elif first_line == 'yes' and len(lines) >= 2:
            return 'Yes\n' + ' '.join(lines[1].split())
        else:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not identity.get('possible', False):
            return solution.strip().lower() == 'no'
        else:
            lines = solution.strip().split('\n')
            if len(lines) < 1 or lines[0].lower() != 'yes':
                return False
            if len(lines) < 2:
                return False
            p_str = lines[1].strip()
            try:
                p = list(map(int, p_str.split()))
            except:
                return False
            n = identity['n']
            if len(p) != n - 1:
                return False
            children = defaultdict(list)
            valid = True
            for i in range(2, n + 1):
                parent = p[i-2]
                if parent < 1 or parent >= i:
                    valid = False
                children[parent].append(i)
            if not valid:
                return False
            subtree_sizes = [1] * (n + 1)
            for node in range(n, 0, -1):
                for child in children.get(node, []):
                    subtree_sizes[node] += subtree_sizes[child]
            total_sum = sum(subtree_sizes)
            if total_sum != identity['s']:
                return False
            max_degree = max((len(v) for v in children.values()), default=0)
            if max_degree != identity.get('k', 0):
                return False
            return True
    
    # 其他额外方法

