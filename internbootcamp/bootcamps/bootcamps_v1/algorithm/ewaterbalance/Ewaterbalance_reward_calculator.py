import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from decimal import Decimal
from decimal import getcontext

# === 源文件中的全局变量 ===

getcontext().prec = 20  # 设置高精度计算环境


class EwaterbalanceRewardCalculator(BaseRewardCalculator):
    """Ewaterbalance奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        
        answer_block = matches[-1].strip()
        solution = []
        for line in answer_block.split('\n'):
            line = line.strip()
            if not line:
                continue
            # 严格格式验证：必须符合xxx.xxxxxxxxx格式
            if not re.fullmatch(r'\d+\.\d{9}', line):
                return None
            solution.append(line)
        
        return solution if len(solution) > 0 else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 使用Decimal进行高精度计算
        n = identity['n']
        a = identity['a']
        
        # 生成参考解
        prefix = [Decimal(0)]
        for num in a:
            prefix.append(prefix[-1] + Decimal(num))
        
        stack = []
        for i in range(n):
            # 当前区间为[i, i+1)
            stack.append((i, i+1))
            while len(stack) >= 2:
                # 比较最后两个区间的平均值
                (i1, j1), (i2, j2) = stack[-2], stack[-1]
                # 计算总水量和长度
                sum1 = prefix[j1] - prefix[i1]
                len1 = j1 - i1
                sum2 = prefix[j2] - prefix[i2]
                len2 = j2 - i2
                # 交叉相乘比较以避免除法误差
                if sum1 * len2 > sum2 * len1:  # 等价于 avg1 > avg2
                    # 合并区间
                    merged = (i1, j2)
                    stack.pop()
                    stack.pop()
                    stack.append(merged)
                else:
                    break
        
        # 生成正确结果
        correct = []
        for i, j in stack:
            avg = (prefix[j] - prefix[i]) / (j - i)
            correct.extend([avg] * (j - i))
        
        # 验证答案
        if len(solution) != len(correct):
            return False
        
        try:
            for user_val, correct_val in zip(solution, correct):
                user_dec = Decimal(user_val)
                # 计算允许误差
                max_denom = max(Decimal(1), abs(correct_val))
                error = abs(user_dec - correct_val)
                if error / max_denom > Decimal('1e-9'):
                    return False
        except:
            return False
        
        return True
    
    # 其他额外方法

