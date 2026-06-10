import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def generate_answer(n, k, p):
    assigned = [0] * 256
    key = list(range(256))
    ans = [0] * n

    for i in range(n):
        cur = p[i]
        if assigned[cur]:
            ans[i] = key[cur]
            continue

        foundkey = False
        no1 = True
        rep = -1
        repb = -1
        start_search = max(0, cur - k + 1)
        
        # 扫描可能的区间
        for it in range(cur, start_search - 1, -1):
            if assigned[it]:
                no1 = False
                if key[it] == it:  # 有效锚点
                    foundkey = True
                    rep = it
                    break
            elif no1:
                repb = it

        if not foundkey:
            # 处理255边界
            group_start = max(0, repb)
            group_end = min(255, group_start + k - 1)
            for it in range(group_start, group_end + 1):
                assigned[it] = 1
                key[it] = group_start
            ans[i] = group_start
        else:
            group_end = min(255, rep + k - 1)
            for it in range(rep, group_end + 1):
                assigned[it] = 1
                key[it] = rep
            ans[i] = rep

    return ans


class CposterizedRewardCalculator(BaseRewardCalculator):
    """Cposterized奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\][\n\s]*((?:-?\d+[\s\n]*)+)[\n\s]*\[/answer\]', output)
        if not matches:
            return None
        try:
            last_match = matches[-1].replace('\n', ' ').strip()
            return list(map(int, last_match.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 严格验证数组长度
            if len(solution) != identity['n']:
                return False
            # 类型一致性检查
            if not all(isinstance(x, int) for x in solution):
                return False
            return solution == identity['ans']
        except:
            return False
    
    # 其他额外方法

