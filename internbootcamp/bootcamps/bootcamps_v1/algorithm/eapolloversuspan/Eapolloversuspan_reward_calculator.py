import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, array):
    if n == 0:
        return 0
    a = array
    b = [format(x, 'b')[::-1] for x in a]
    lens = [len(x) for x in b]
    maxK = max(lens) if lens else 0
    bcnt = [0] * maxK
    for i in range(n):
        x = b[i]
        for k in range(len(x)):
            if x[k] == '1':
                if k >= len(bcnt):
                    bcnt += [0] * (k - len(bcnt) + 1)
                bcnt[k] += 1
    kpowb = [ ((1 << k) % MOD) * bcnt[k] % MOD for k in range(len(bcnt)) ]
    summ = sum(kpowb) % MOD
    ans = 0
    for j in range(n):
        xj = a[j] % MOD
        x_bits = b[j]
        tmp = 0
        for k in range(len(x_bits)):
            if x_bits[k] == '1' and k < len(kpowb):
                tmp = (tmp + kpowb[k]) % MOD
        term_part = ( (xj * n) % MOD + (summ - tmp) % MOD ) % MOD
        term = (tmp * term_part) % MOD
        ans = (ans + term) % MOD
    return ans


class EapolloversuspanRewardCalculator(BaseRewardCalculator):
    """Eapolloversuspan奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 更健壮的正则表达式
        matches = re.findall(
            r'\[answer\][\s\n]*(-?\d+)[\s\n]*\[/answer\]', 
            output, 
            re.IGNORECASE | re.DOTALL
        )
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = compute_answer(identity['n'], identity['array'])
            user_ans = int(solution) % MOD
            return user_ans == expected % MOD
        except:
            return False
    
    # 其他额外方法

