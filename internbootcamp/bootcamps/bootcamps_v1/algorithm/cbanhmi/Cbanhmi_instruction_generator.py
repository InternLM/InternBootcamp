import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CbanhmiInstructionGenerator(BaseInstructionGenerator):
    """Cbanhmi Bootcamp指令生成器"""
    
    def __init__(self, n=None, q=2, min_n=4, max_n=10):
        """
        初始化Cbanhmi指令生成器
        
        Args:
            n: 参数描述
            q: 参数描述
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数说明：
        n    - 固定字符串长度（可选）
        q    - 查询数量（默认2）
        min_n - 最小随机长度（当n未指定时生效）
        max_n - 最大随机长度（当n未指定时生效）
        """
        if n is not None:
            self.n = n
        else:
            self.n = random.randint(min_n, max_n)
        self.q = q
    
    def case_generator(self):
        """生成具有边界覆盖的测试案例"""
        # 生成字符串（20%概率全0/全1）
        if random.random() < 0.2:
            s = '0' * self.n if random.choice([True, False]) else '1' * self.n
        else:
            s = ''.join(random.choices(['0','1'], weights=[7,3], k=self.n))
        
        # 预处理前缀和
        cnt1 = [0]*(self.n+1)
        cnt0 = [0]*(self.n+1)
        for i in range(1, self.n+1):
            cnt1[i] = cnt1[i-1] + (1 if s[i-1] == '1' else 0)
            cnt0[i] = cnt0[i-1] + (1 if s[i-1] == '0' else 0)
        
        # 生成多样化查询
        queries = []
        answers = []
        for _ in range(self.q):
            # 30%概率生成全区间查询
            if random.random() < 0.3:
                l, r = 1, self.n
            else:
                l = random.randint(1, self.n)
                r = random.randint(l, self.n)
            
            ones = cnt1[r] - cnt1[l-1]
            zeros = cnt0[r] - cnt0[l-1]
            
            # 动态计算答案
            t1 = (pow(2, ones, MOD) - 1) % MOD
            t2 = ((pow(2, ones, MOD)-1) * (pow(2, zeros, MOD)-1)) % MOD
            ans = (t1 + t2) % MOD
            
            queries.append({'l': l, 'r': r})
            answers.append(ans)
        
        return {
            'n': self.n,
            'q': self.q,
            's': s,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        """生成结构化问题描述"""
        prompt = [
            f"Banh-mi问题求解（n={case['n']}, q={case['q']}）\n\n",
            "字符串：", case['s'], "\n\n",
            "查询列表（格式：l r）：\n"
        ]
        for q in case['queries']:
            prompt.append(f"{q['l']} {q['r']}\n")
        prompt.append("\n请逐行输出每个查询的结果，用[answer]包裹，如：\n[answer]答案[/answer]")
        return ''.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

