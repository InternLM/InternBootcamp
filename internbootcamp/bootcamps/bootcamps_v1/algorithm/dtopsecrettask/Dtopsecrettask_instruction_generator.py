import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_loquacity(n, k, s, q):
    adjusted_s = min(s, (n*n)//2 + 10)  # 严格模拟参考代码的调整逻辑
    INF = float('inf')
    
    # 初始化DP数组，使用滚动数组优化
    dp = [[[INF] * (adjusted_s + 1) for _ in range(k+1)] for __ in range(2)]
    dp[0][0][0] = 0  # 初始状态

    for i in range(1, n+1):
        current = i % 2
        prev = 1 - current
        
        # 重置当前层
        for j in range(k+1):
            for t in range(adjusted_s + 1):
                dp[current][j][t] = INF
        
        # 状态转移
        for pref in range(0, min(i-1, k)+1):
            for done in range(adjusted_s + 1):
                if dp[prev][pref][done] == INF:
                    continue
                
                # 情况1：不选当前士兵
                if dp[current][pref][done] > dp[prev][pref][done]:
                    dp[current][pref][done] = dp[prev][pref][done]
                
                # 情况2：选当前士兵
                new_pref = pref + 1
                if new_pref > k:
                    continue
                
                swaps_needed = i - new_pref  # 与参考代码完全一致的计算方式
                new_done = done + swaps_needed
                
                if new_done <= adjusted_s:
                    new_value = dp[prev][pref][done] + q[i-1]
                    if new_value < dp[current][new_pref][new_done]:
                        dp[current][new_pref][new_done] = new_value
        
    # 寻找最终答案
    final_layer = n % 2
    return min(dp[final_layer][k][:adjusted_s+1])


class DtopsecrettaskInstructionGenerator(BaseInstructionGenerator):
    """Dtopsecrettask Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dtopsecrettask指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        # 参数校验确保合法性
        self.params.setdefault('min_n', 3)
        self.params.setdefault('max_n', 150)
        self.params.setdefault('min_k', 1)
        self.params.setdefault('max_k', 150)
        self.params.setdefault('min_s', 1)
        self.params.setdefault('max_s', 10**9)
        self.params.setdefault('q_min', 1)
        self.params.setdefault('q_max', 10**6)

        # 确保参数间约束关系
        self.params['min_n'] = max(self.params['min_n'], 1)
        self.params['max_n'] = min(self.params['max_n'], 150)
        self.params['min_k'] = max(self.params['min_k'], 1)
        self.params['max_k'] = min(self.params['max_k'], self.params['max_n'])
    
    def case_generator(self):
        # 确保k <= n的约束
        n = random.randint(self.params['min_n'], self.params['max_n'])
        k = random.randint(
            self.params['min_k'], 
            min(n, self.params['max_k'])
        )
        s = random.randint(self.params['min_s'], self.params['max_s'])
        
        # 生成loquacity值时保证至少k个非极大值
        q = [
            random.randint(self.params['q_min'], self.params['q_max'])
            for _ in range(n)
        ]
        # 插入k个较小值以确保有解
        for _ in range(k):
            q[random.randint(0, n-1)] = random.randint(
                self.params['q_min'], 
                self.params['q_max']//100
            )
        
        return {
            'n': n,
            'k': k,
            's': s,
            'q': q,
            'expected': calculate_min_loquacity(n, k, s, q)
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""作为军事参谋，你需要解决秘密部队优化问题。请根据以下输入数据计算最小loquacity总和：

输入格式：
第一行：n k s
第二行：q1 q2 ... qn

当前输入：
{question_case['n']} {question_case['k']} {question_case['s']}
{' '.join(map(str, question_case['q']))}

要求：
1. 最多进行s次相邻交换
2. 最终前k个士兵的loquacity总和最小
3. 答案需用[answer]标签包裹，如：[answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

