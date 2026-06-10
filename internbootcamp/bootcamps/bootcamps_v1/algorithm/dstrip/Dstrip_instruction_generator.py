import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import inf

# === 源文件中的全局函数 ===

def _test():
    bootcamp = Dstripbootcamp(ensure_solvable=True)
    case = bootcamp.case_generator()
    print("Generated case:", case)
    print("Prompt:\n", bootcamp.prompt_func(case))
    
    # 测试解法
    assert bootcamp._verify_correction(case['correct_answer'], case), "Validation failed"


class DstripInstructionGenerator(BaseInstructionGenerator):
    """Dstrip Bootcamp指令生成器"""
    
    def __init__(self, min_n=5, max_n=15, min_s=1, max_s=20, min_l=2, max_l=5, ensure_solvable=False):
        """
        初始化Dstrip指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_s: 参数描述
            max_s: 参数描述
            min_l: 参数描述
            max_l: 参数描述
            ensure_solvable: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 参数有效性验证
        assert min_l <= max_l <= max_n, "Invalid length constraints"
        self.min_n = min_n
        self.max_n = max_n
        self.min_s = min_s
        self.max_s = max_s
        self.min_l = min_l
        self.max_l = max_l
        self.ensure_solvable = ensure_solvable
    
    def case_generator(self):
        for _ in range(1000):  # 防止无限循环
            n = random.randint(self.min_n, self.max_n)
            l = random.randint(self.min_l, min(self.max_l, n))
            s = random.randint(self.min_s, self.max_s)
            
            # 生成有效数组的三种模式
            if random.random() < 0.3 and self.ensure_solvable:
                # 模式1：保证有解的序列（分段生成）
                a = []
                remaining = n
                while remaining > 0:
                    seg_len = random.randint(l, min(3*l, remaining))
                    base = random.randint(0, 50)
                    a.extend([base + random.randint(0, s) for _ in range(seg_len)])
                    remaining -= seg_len
                random.shuffle(a)
            elif random.random() < 0.5:
                # 模式2：随机数组带验证
                a = [random.randint(0, 100) for _ in range(n)]
            else:
                # 模式3：刻意构造无解情况
                a = [0]*(l-1) + [100]*(n-l+1)
                s = 10
                l += 1  # 确保无法满足长度要求
                
            # 计算正确答案
            dp = [inf] * (n+1)
            dp[0] = 0
            for i in range(1, n+1):
                for j in range(max(0, i-3*l), i-l+1):
                    if j < 0: continue
                    seg = a[j:i]
                    if max(seg)-min(seg) <= s:
                        dp[i] = min(dp[i], dp[j]+1)
            ans = dp[n] if dp[n] != inf else -1
            
            # 二次验证
            if self.ensure_solvable and ans == -1:
                continue
            if not self.ensure_solvable and ans != -1:
                # 反向验证无解情况
                if all(max(a[i:i+l]) - min(a[i:i+l]) > s for i in range(n-l+1)):
                    ans = -1
            return {
                'n': n, 's': s, 'l': l,
                'a': a, 'correct_answer': ans
            }
        raise RuntimeError("Failed to generate valid case")
    
    @staticmethod
    def prompt_func(case):
        return (
            f"Split the sequence into minimal pieces where each:\n"
            f"- Contains ≥{case['l']} numbers\n- Max-min ≤{case['s']}\n\n"
            f"Input:\n{case['n']} {case['s']} {case['l']}\n"
            f"{' '.join(map(str, case['a']))}\n\n"
            "Output the minimal number of pieces or -1 if impossible.\n"
            "Format: [answer]result[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

