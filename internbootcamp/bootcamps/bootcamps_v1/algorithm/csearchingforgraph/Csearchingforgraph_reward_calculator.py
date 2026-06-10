import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple




class CsearchingforgraphRewardCalculator(BaseRewardCalculator):
    """Csearchingforgraph奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[List[str]]:
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        return lines if lines else None
    
    @classmethod
    def _verify_correction(cls, solution: List[str], identity: Dict[str, Any]) -> bool:
        try:
            # Step 1: Parse user's solution
            all_edges = []
            for line in solution:
                a, b = sorted(map(int, line.strip().split()))
                if a == b or a < 1:
                    return False
                all_edges.append((a, b))
            
            # Check for duplicates
            if len(all_edges) != len(set(all_edges)):
                return False

            edge_ptr = 0
            # Process each test case
            for test_case in identity['tests']:
                n = test_case['n']
                p = test_case['p']
                required = 2 * n + p
                available = len(all_edges) - edge_ptr
                
                # Check if enough edges
                if available < required:
                    return False
                
                # Extract edges for this test case
                test_edges = set(all_edges[edge_ptr:edge_ptr+required])
                edge_ptr += required
                
                # Validate edges are within vertex range
                for a, b in test_edges:
                    if b > n or a > n:
                        return False
                
                # Generate canonical solution
                canonical_edges = set()
                want = required
                for i in range(n):
                    if want <= 0:
                        break
                    for j in range(i+1, n):
                        if want <= 0:
                            break
                        canonical_edges.add((i+1, j+1))
                        want -= 1
                
                # Compare edge sets
                if test_edges != canonical_edges:
                    # Check if alternative valid structure exists
                    total_edges = len(test_edges)
                    if total_edges != required:
                        return False
                    
                    # Validate subgraph conditions (basic check for small n)
                    if n <= 10:
                        adj = {v: set() for v in range(1, n+1)}
                        for a, b in test_edges:
                            adj[a].add(b)
                            adj[b].add(a)
                        
                        from itertools import combinations
                        valid = True
                        for k in range(1, n+1):
                            max_allowed = 2 * k + p
                            # Check all k-combinations of vertices
                            for vertices in combinations(range(1, n+1), k):
                                sub_edges = 0
                                for i in range(len(vertices)):
                                    for j in range(i+1, len(vertices)):
                                        if vertices[j] in adj[vertices[i]]:
                                            sub_edges += 1
                                if sub_edges > max_allowed:
                                    valid = False
                                    break
                            if not valid:
                                return False
            return edge_ptr == len(all_edges)
        except Exception:
            return False
    
    # 其他额外方法

