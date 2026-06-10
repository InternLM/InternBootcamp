import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_min_difference(n, p, k_list):
    if p == 1:
        return (n % 2) % MOD
    
    val = defaultdict(int)
    for k in k_list:
        val[k] += 1

    v = sorted(val.keys())
    F = []
    S = []

    # 计算最大有效指数差
    lg = 0
    x = 1
    while x < 1e6 and p > 1:
        x *= p
        lg += 1

    rr = len(v) - 1
    while rr >= 0:
        current_k = v[rr]
        if val[current_k] <= 0:
            rr -= 1
            continue
        
        # 处理偶数情况
        if val[current_k] % 2 == 0:
            val[current_k] = 0
            rr -= 1
            continue
        
        # 处理奇数情况
        val[current_k] = 0
        lp = rr - 1
        while lp >= 0 and val[v[lp]] <= 0:
            lp -= 1
        
        # 没有可配对元素
        if lp < 0:
            F.append((current_k, 1))
            break
        
        # 判断指数差是否可合并
        need_steps = current_k - v[lp]
        if need_steps > lg:
            F.append((current_k, 1))
            break
        
        # 计算需要合并的数量
        need = p ** need_steps
        flag = True
        original_lp = lp
        
        # 合并操作
        while lp >= 0 and flag:
            current_lp_k = v[lp]
            
            if need > 1e6:
                flag = False
                break
            
            if val[current_lp_k] >= need:
                val[current_lp_k] -= need
                need = 0
                break
            else:
                need -= val[current_lp_k]
                val[current_lp_k] = 0
                
                if lp == 0:
                    flag = False
                    break
                
                # 计算下一级指数差
                step = current_lp_k - v[lp-1]
                if step > lg:
                    flag = False
                    break
                
                need *= p ** step
                lp -= 1
        
        if not flag or lp < 0:
            F.append((current_k, 1))
            break
        
        # 清理中间元素
        for j in range(lp + 1, original_lp + 1):
            val[v[j]] = 0
    
    # 收集剩余元素
    for k in v:
        if val[k] > 0:
            S.append((k, val[k]))
    
    # 计算最终结果
    sum_F = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in F) % MOD
    sum_S = sum(pow(p, k, MOD) * cnt % MOD for k, cnt in S) % MOD
    return abs(sum_F - sum_S) % MOD


class EjohnnyandgrandmasterRewardCalculator(BaseRewardCalculator):
    """Ejohnnyandgrandmaster奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强提取逻辑的鲁棒性
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 添加类型转换容错
        try:
            return int(solution) == identity['expected_answer']
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

