import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EjohnnyandgrandmasterInstructionGenerator(BaseInstructionGenerator):
    """Ejohnnyandgrandmaster Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, max_p=10**6, max_k=1000):
        """
        初始化Ejohnnyandgrandmaster指令生成器
        
        Args:
            max_n: 参数描述
            max_p: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数优化：增加有效取值范围
        - 支持生成n=1的边界情况
        - 允许k=0的特殊指数
        - 覆盖大p和小p的组合
        """
        self.max_n = max_n
        self.max_p = max_p
        self.max_k = max_k
    
    def case_generator(self):
        # 生成参数时增加特例概率
        p = random.choice([
            random.randint(1, 10),
            random.randint(10**5, 10**6),
            1  # 特殊case概率提升
        ])
        
        # 控制n的取值范围
        n = random.choice([
            random.randint(1, 10),
            random.randint(1, self.max_n),
            1  # 单元素case
        ])
        
        # k生成策略优化
        k_list = random.choices(
            population=[0, 1, random.randint(2, 10), random.randint(10, self.max_k)],
            weights=[0.2, 0.2, 0.3, 0.3],
            k=n
        )
        
        # 计算预期答案
        expected = compute_min_difference(n, p, k_list)
        return {
            'n': n,
            'p': p,
            'k_list': k_list,
            'expected_answer': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        # 增强提示信息的格式要求
        return f"""你需要将{pow(question_case['p'], question_case['k_list'][0]) if question_case['k_list'] else 0}等数值分成两个集合，使得两集合和的绝对差最小。参数：
n={question_case['n']}, p={question_case['p']}, k列表={question_case['k_list']}

请将答案数值（取模后的结果）放在[answer]标签内，例如：[answer]12345[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

