import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CsecretRewardCalculator(BaseRewardCalculator):
    """Csecret奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强格式容错性
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL|re.IGNORECASE)
        if not matches:
            return None
        solution = matches[-1].strip().replace(',', ' ').replace('\n', ' ')
        solution = ' '.join(solution.split())
        
        if solution == '-1':
            return '-1'
        
        if re.fullmatch(r'(-1)|((\d+ )*\d+)', solution) and len(solution.split()) == solution.count(' ') + 1:
            return solution
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n, k = identity['n'], identity['k']
        minimal_condition = 3*k <= n  # 存在解的必要条件
        
        # 类型判断
        if solution == '-1':
            return not minimal_condition  # 当且仅当无解时返回-1正确
        
        if not minimal_condition:
            return False  # 当必须无解时却返回解
        
        # 格式验证
        try:
            parts = list(map(int, solution.split()))
            if len(parts) != n or any(p < 1 or p > k for p in parts):
                return False
        except:
            return False
        
        # 构建分配字典
        allocation = [[] for _ in range(k)]
        for idx, keeper in enumerate(parts, 1):  # 单词编号从1开始
            allocation[keeper-1].append(idx)
        
        # 完整性检查
        all_words = {w for group in allocation for w in group}
        if all_words != set(range(1, n+1)):
            return False
        
        # 集合属性验证
        for group in allocation:
            if len(group) < 3:
                return False
            
            sorted_group = sorted(group)
            d = sorted_group[1] - sorted_group[0]
            # 快速检测等差数列
            for i in range(2, len(sorted_group)):
                if sorted_group[i] - sorted_group[i-1] != d:
                    break
            else:
                # 全部差值相同则失败
                return False
        
        return True
    
    # 其他额外方法

