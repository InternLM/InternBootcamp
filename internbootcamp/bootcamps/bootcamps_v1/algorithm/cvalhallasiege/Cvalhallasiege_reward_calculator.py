import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CvalhallasiegeRewardCalculator(BaseRewardCalculator):
    """Cvalhallasiege奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        last_answer = matches[-1].strip()
        solution = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line and line.isdigit():
                solution.append(int(line))
        
        return solution  # 移除了错误的条件判断
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        k_list = identity['k']
        sum_a = identity['sum_a']
        n = identity['n']
        q = identity['q']
        
        if len(solution) != q:
            return False
        
        psum = [0] * (n + 1)
        for i in range(1, n+1):
            psum[i] = psum[i-1] + a[i-1]
        
        def binary_search(s_val):
            low, high = 0, n
            while low <= high:
                mid = (low + high) // 2
                if psum[mid] > s_val:
                    high = mid - 1
                else:
                    low = mid + 1
            return high  # 正确的二分查找逻辑
        
        s = 0
        correct = []
        for k in k_list:
            s += k
            if s >= sum_a:
                correct.append(n)
                s = 0
            else:
                p = binary_search(s)
                correct.append(n - p)
        
        return solution == correct
    
    # 其他额外方法

