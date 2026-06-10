import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import math
from itertools import combinations




class FaupontrougeRewardCalculator(BaseRewardCalculator):
    """Faupontrouge奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # Reimplement C++ logic for validation
            s = identity['s']
            m = identity['m']
            k = identity['k']
            n = len(s)

            # Build trie structure
            nodes = [cls.TreeNode()]
            for i in range(n):
                cur = 0
                nodes[cur].have += (n - i)
                for j in range(i, n):
                    c = ord(s[j]) - ord('a')
                    if nodes[cur].nxt[c] == -1:
                        nodes.append(cls.TreeNode())
                        nodes[cur].nxt[c] = len(nodes) - 1
                        nodes[-1].nxt = [-1]*26
                    cur = nodes[cur].nxt[c]
                    nodes[cur].have += (n - j)
                    nodes[cur].interm += 1

            # Binary search with DP verification
            left, right = 0, (n * (n + 1)) // 2
            answer = ""
            while left < right:
                mid = (left + right + 1) // 2
                candidate = cls.find_in_trie(nodes, mid)
                if cls.check_valid(s, k, candidate, m):
                    left = mid
                    answer = candidate
                else:
                    right = mid - 1
            return solution == answer
        except:
            return False
    
    # 其他额外方法

