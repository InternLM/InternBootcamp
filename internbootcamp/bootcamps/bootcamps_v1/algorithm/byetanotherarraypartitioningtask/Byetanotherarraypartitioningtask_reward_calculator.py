import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class ByetanotherarraypartitioningtaskRewardCalculator(BaseRewardCalculator):
    """Byetanotherarraypartitioningtask奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = [line.strip() for line in last_match.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            sum_answer = int(lines[0])
            partitions = list(map(int, lines[1].split()))
        except:
            return None
        return (sum_answer, partitions)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != 2:
            return False
        sum_user, partitions = solution
        k = identity['k']
        n = identity['n']
        m = identity['m']
        # 检查总和是否正确
        if sum_user != identity['sum_answer']:
            return False
        # 检查分割点数量
        if len(partitions) != k - 1:
            return False
        # 检查分割点是否递增且在合理范围
        prev = 0
        for p in partitions:
            if p <= prev or p < 1 or p >= n:
                return False
            prev = p
        # 检查每个子数组长度至少m
        current_start = 0
        for p in partitions + [n]:
            sub_length = p - current_start
            if sub_length < m:
                return False
            current_start = p
        # 检查实际总和是否匹配
        current_start = 0
        total = 0
        a = identity['a']
        for p in partitions + [n]:
            sub = a[current_start:p]
            sorted_sub = sorted(sub, reverse=True)
            total += sum(sorted_sub[:m])
            current_start = p
        return total == sum_user
    
    # 其他额外方法

