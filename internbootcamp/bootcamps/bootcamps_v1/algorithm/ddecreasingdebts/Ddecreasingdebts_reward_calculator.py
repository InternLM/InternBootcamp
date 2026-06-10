import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re




class DdecreasingdebtsRewardCalculator(BaseRewardCalculator):
    """Ddecreasingdebts奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        try:
            m_prime = int(lines[0])
        except:
            return None
        if len(lines) != m_prime + 1:
            return None
        debts = []
        seen = set()
        for line in lines[1:]:
            parts = line.split()
            if len(parts) !=3:
                return None
            try:
                u = int(parts[0])
                v = int(parts[1])
                d = int(parts[2])
                # 检查是否科学计数法（如1e5）
                if 'e' in line.lower():
                    return None
            except:
                return None
            if u == v or d <=0 or (u, v) in seen:
                return None
            seen.add((u, v))
            debts.append((u, v, d))
        return debts
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            expected_total = identity['expected_total']
            return expected_total == 0
        input_info = identity['input']
        n = input_info['n']
        original_net = identity['original_net']
        expected_total = identity['expected_total']
        
        # 验证solution的格式
        seen = set()
        current_total =0
        solution_net = [0]*(n+1)
        for u, v, d in solution:
            if u == v or d <=0 or (u, v) in seen:
                return False
            seen.add((u, v))
            solution_net[u] += d
            solution_net[v] -= d
            current_total +=d
        
        # 验证净债务是否一致
        for i in range(1, n+1):
            if solution_net[i] != original_net[i]:
                return False
        
        # 验证总债务是否正确
        return current_total == expected_total
    
    # 其他额外方法

