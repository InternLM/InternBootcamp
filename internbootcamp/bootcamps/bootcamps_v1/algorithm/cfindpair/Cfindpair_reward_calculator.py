import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_kth_pair(n, k, array):
    vs = sorted(array)  # 确保排序逻辑正确
    p = k - 1
    lenvs = len(vs)
    
    # 处理极端情况
    if lenvs == 0: return (None, None)
    if lenvs == 1: return (vs[0], vs[0])
    
    # 主计算逻辑
    prow = p // lenvs
    vrow = vs[prow]
    
    # 寻找连续元素块边界
    prow0 = prow
    while prow0 > 0 and vs[prow0-1] == vrow:
        prow0 -= 1
    prow1 = prow + 1
    while prow1 < lenvs and vs[prow1] == vrow:
        prow1 += 1
    
    # 计算有效块尺寸
    block_size = prow1 - prow0
    block_start_index = prow0 * lenvs
    
    # 剩余位置计算
    remaining = p - block_start_index
    if remaining < 0:
        return (vs[p//lenvs], vs[p%lenvs])
    
    # 计算列位置
    col = remaining // block_size
    return (vrow, vs[col])


class CfindpairRewardCalculator(BaseRewardCalculator):
    """Cfindpair奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强匹配鲁棒性，允许任意空白符
        pattern = r'\[answer\]\s*(-?\d+)\s+(-?\d+)\s*\[/answer\]'
        matches = re.findall(pattern, output)
        if not matches:
            return None
        last_match = matches[-1]
        try:
            return (int(last_match[0]), int(last_match[1]))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            k = identity['k']
            array = identity['array']
            expected = compute_kth_pair(n, k, array)
            return solution == expected
        except Exception as e:
            return False
    
    # 其他额外方法

