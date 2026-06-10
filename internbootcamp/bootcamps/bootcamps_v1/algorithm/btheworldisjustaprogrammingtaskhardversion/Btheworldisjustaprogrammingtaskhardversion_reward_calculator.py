import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_balance_and_count(s):
    balance = 0
    min_balance = 0
    count = 0
    prefix = []
    for c in s:
        balance += 1 if c == '(' else -1
        prefix.append(balance)
        if balance < min_balance:
            min_balance = balance
            count = 1
        elif balance == min_balance:
            count += 1
    return min_balance, count, prefix

def calculate_real_beauty(s):
    total = sum(1 if c == '(' else -1 for c in s)
    if total != 0:
        return 0
    min_balance, count, prefix = compute_min_balance_and_count(s)
    overall_min = min(prefix)
    if overall_min < 0:
        return 0
    return count

def optimal_solution(n, s):
    max_beauty = 0
    best_pair = (1, 1)
    original_beauty = calculate_real_beauty(s)
    max_beauty = original_beauty
    
    s_list = list(s)
    for i in range(n):
        for j in range(i, n):
            if s_list[i] == s_list[j]:
                continue
            
            # Perform swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
            new_s = ''.join(s_list)
            current_beauty = calculate_real_beauty(new_s)
            
            if current_beauty > max_beauty:
                max_beauty = current_beauty
                best_pair = (i+1, j+1)
            
            # Revert swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
    
    return (max_beauty, best_pair[0], best_pair[1])


class BtheworldisjustaprogrammingtaskhardversionRewardCalculator(BaseRewardCalculator):
    """Btheworldisjustaprogrammingtaskhardversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        try:
            if len(lines) >= 2:
                max_val = int(lines[0])
                l, r = map(int, lines[1].split())
                return (max_val, l, r)
        except:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != 3:
            return False
        max_val, l, r = solution
        
        # 验证基础参数
        if max_val != identity['expected_max']:
            return False
        if not (1 <= l <= identity['n'] and 1 <= r <= identity['n']):
            return False
        
        # 执行交换操作
        s_list = list(identity['s'])
        l_idx, r_idx = l-1, r-1
        s_list[l_idx], s_list[r_idx] = s_list[r_idx], s_list[l_idx]
        new_s = ''.join(s_list)
        
        # 计算实际美丽值
        actual_beauty = calculate_real_beauty(new_s)
        
        # 允许误差处理（应对计算误差）
        return actual_beauty == max_val
    
    # 其他额外方法

