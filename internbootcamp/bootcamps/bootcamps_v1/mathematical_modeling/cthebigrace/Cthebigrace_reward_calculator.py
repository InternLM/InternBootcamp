import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from math import gcd

# === 源文件中的全局函数 ===

def compute_probability(t, w, b):
    """优化边界条件处理和极值计算逻辑"""
    if t == 0:
        return (0, 1)
    
    # 计算最大公约数和最小公倍数
    gcd_val = gcd(w, b)
    lcm = (w * b) // gcd_val
    
    # 处理超大数值的溢出保护
    try:
        full_cycles = t // lcm
        remaining = t % lcm
    except:
        return (0, 1)
    
    min_step = min(w, b)
    count = (full_cycles + 1) * min_step - 1
    
    # 调整剩余部分
    if remaining < min_step - 1:
        count -= (min_step - 1 - remaining)
    
    # 结果规范化
    count = max(0, count)  # 确保非负
    total_gcd = gcd(count, t)
    
    return (count // total_gcd, t // total_gcd)


class CthebigraceRewardCalculator(BaseRewardCalculator):
    """Cthebigrace奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强格式兼容性的正则表达式
        pattern = r'(?:\[answer\]|ANSWER:?)\s*(\d+)\s*/\s*(\d+)\s*(?:\[/answer\]|)'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            last_p, last_q = matches[-1]
            try:
                p = int(last_p)
                q = int(last_q)
                if q > 0 and p >= 0:
                    return f"{p}/{q}"
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        try:
            p_user, q_user = map(int, solution.split('/'))
            if q_user <= 0 or p_user < 0:
                return False
        except:
            return False
        
        try:
            p_correct, q_correct = compute_probability(
                identity['t'],
                identity['w'],
                identity['b']
            )
        except:
            return False
        
        return p_user == p_correct and q_user == q_correct
    
    # 其他额外方法

