import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
from functools import reduce
from collections import deque

# === 源文件中的全局函数 ===

def lcm(a, b):
    return a * b // math.gcd(a, b)

def solve_case(n, m, edges):
    try:
        # 预处理阶段增加输入合法性校验
        for u, v, g, l in edges:
            if g > l or l % g != 0:
                return (False, None)
            if math.gcd(g, l//g) != 1:
                return (False, None)

        a0 = [1] * n
        # 构建a0阶段
        for u, v, g, _ in edges:
            a0[u-1] = lcm(a0[u-1], g)
            a0[v-1] = lcm(a0[v-1], g)

        # 构建关系图
        adjacency = [[] for _ in range(n)]
        for u, v, g, l in edges:
            u_idx, v_idx = u-1, v-1
            k_base = lcm(a0[u_idx], a0[v_idx])
            if l % k_base != 0:
                return (False, None)
            k = l // k_base
            adjacency[u_idx].append((v_idx, k, g))
            adjacency[v_idx].append((u_idx, k, g))

        # 连通分量处理
        solution = [1] * n
        visited = [False] * n
        for i in range(n):
            if visited[i]:
                continue
                
            # BFS遍历连通分量
            q = deque([i])
            visited[i] = True
            divisors = []
            for node in q:
                for _, k, _ in adjacency[node]:
                    divisors.append(k)
            
            # 计算最大公约数
            base_divisor = reduce(math.gcd, divisors, 0) if divisors else 1
            
            # 寻找有效因子
            found = False
            for d in range(1, base_divisor + 1):
                if base_divisor % d != 0:
                    continue
                    
                temp_sol = {i: d}
                valid = True
                bfs_q = deque([i])
                
                while bfs_q and valid:
                    current = bfs_q.popleft()
                    current_d = temp_sol[current]
                    
                    for neighbor, k, g in adjacency[current]:
                        required = k // current_d
                        
                        if neighbor in temp_sol:
                            if temp_sol[neighbor] != required:
                                valid = False
                                break
                            continue
                            
                        if k % current_d != 0:
                            valid = False
                            break
                            
                        # 验证边条件
                        a_val = a0[current] * current_d
                        b_val = a0[neighbor] * required
                        if math.gcd(a_val, b_val) != g or lcm(a_val, b_val) != (a_val * b_val) // g:
                            valid = False
                            break
                            
                        temp_sol[neighbor] = required
                        bfs_q.append(neighbor)
                        
                if valid:
                    for node in temp_sol:
                        solution[node] = temp_sol[node]
                    found = True
                    break
                    
            if not found:
                return (False, None)

        # 最终有效性检查
        final = [a0[i] * solution[i] for i in range(n)]
        for num in final:
            if not (1 <= num <= 10**6):
                return (False, None)
                
        for u, v, g, l in edges:
            a, b = final[u-1], final[v-1]
            if math.gcd(a, b) != g or lcm(a, b) != l:
                return (False, None)
                
        return (True, final)
        
    except:
        return (False, None)


class CmushroomstrifeRewardCalculator(BaseRewardCalculator):
    """Cmushroomstrife奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', text, re.DOTALL)
        if not matches:
            return None
            
        answer = matches[-1].strip().upper()
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        
        if not lines:
            return None
            
        if lines[0] == 'NO' and len(lines) == 1:
            return 'NO'
            
        if lines[0] == 'YES' and len(lines) >= 2:
            try:
                numbers = list(map(int, lines[1].split()))
                return numbers
            except:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        # 严格类型检查
        if isinstance(solution, list):
            if len(solution) != case["n"]:
                return False
            try:
                nums = list(map(int, solution))
                if any(not (1 <= x <= 10**6) for x in nums):
                    return False
            except:
                return False
            
            for u, v, g, l in case["edges"]:
                a, b = nums[u-1], nums[v-1]
                actual_gcd = math.gcd(a, b)
                actual_lcm = (a * b) // actual_gcd
                if actual_gcd != g or actual_lcm != l:
                    return False
            return True
            
        elif solution == 'NO':
            possible, _ = solve_case(case["n"], case["m"], case["edges"])
            return not possible
            
        return False
    
    # 其他额外方法

