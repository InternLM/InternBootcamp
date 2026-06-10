import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_prefixes(s):
    sca = [0] * (len(s) + 1)
    scb = [0] * (len(s) + 1)
    for i in range(1, len(s) + 1):
        char = s[i-1]
        if char == 'A':
            sca[i] = sca[i-1] + 1
            scb[i] = scb[i-1]
        else:
            sca[i] = sca[i-1]
            scb[i] = scb[i-1] + 1
    return sca, scb

def compute_query_result(sca, scb, tca, tcb, a, b, c, d):
    sb = scb[b] - scb[a-1]
    sa = min(sca[b], b - a + 1)
    tb = tcb[d] - tcb[c-1]
    ta = min(tca[d], d - c + 1)

    if (sb ^ tb) & 1:
        return '0'
    if sa < ta:
        return '0'
    if (sa - ta) % 3 == 0:
        if sb > tb:
            return '0'
    else:
        if (sb + 2) > tb:
            return '0'
    if sb == 0 and tb != 0 and sa == ta:
        return '0'
    return '1'


class DpickingstringsRewardCalculator(BaseRewardCalculator):
    """Dpickingstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        return matches[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['S']
        t = identity['T']
        queries = identity['queries']
        sca, scb = compute_prefixes(s)
        tca, tcb = compute_prefixes(t)
        expected = []
        for a, b, c, d in queries:
            res = compute_query_result(sca, scb, tca, tcb, a, b, c, d)
            expected.append(res)
        expected_str = ''.join(expected)
        return solution == expected_str
    
    # 其他额外方法

