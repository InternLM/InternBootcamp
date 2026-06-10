import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class CnamingcompanyInstructionGenerator(BaseInstructionGenerator):
    """Cnamingcompany Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cnamingcompany指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """支持动态参数配置"""
        self.n = params.get('n', 7)
        self.seed = params.get('seed', None)
        random.seed(self.seed) if self.seed else None
    
    def case_generator(self):
        """生成多样化测试案例"""
        # 生成原始输入（保持输入顺序）
        s = ''.join(random.choices(string.ascii_lowercase, k=self.n))
        t = ''.join(random.choices(string.ascii_lowercase, k=self.n))
        
        # 确保至少20%概率生成特殊案例
        if random.random() < 0.2:  
            # case1: 全等字符
            if random.choice([True, False]):
                char = random.choice(string.ascii_lowercase)
                return {'s': char*self.n, 't': char*self.n}
            # case2: 极值情况（一方全a一方全z）
            else:
                return {'s': 'a'*self.n, 't': 'z'*self.n}
        return {'s': s, 't': t}
    
    @staticmethod
    def prompt_func(case):
        """生成符合题设要求的完整问题描述"""
        return f"""Oleg和Igor的字母集分别为：
Oleg: {case['s']}
Igor: {case['t']}

根据博弈规则确定最终公司名称，将答案放在[answer]标签内。例如：[answer]abc[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_answer(s, t):
        """与参考算法保持完全一致的实现"""
        first = sorted(s)
        second = sorted(t, reverse=True)
        n = len(first)
        ans = [''] * n

        split = n // 2
        f = first[:split]
        s_part = second[:split]

        if n % 2:
            f.append(first[split])

        l, r = 0, n-1
        fl, fr = 0, len(f)-1
        sl, sr = 0, len(s_part)-1

        for idx in range(n):
            if idx % 2 == 0:  # Oleg's turn
                if idx == n-1:
                    ans[l] = f[fl]
                    break
                if f[fl] >= s_part[sl]:
                    ans[r] = f[fr]
                    r -= 1
                    fr -= 1
                else:
                    ans[l] = f[fl]
                    l += 1
                    fl += 1
            else:  # Igor's turn
                if idx == n-1:
                    ans[l] = s_part[sl]
                    break
                if s_part[sl] <= f[fl]:
                    ans[r] = s_part[sr]
                    r -= 1
                    sr -= 1
                else:
                    ans[l] = s_part[sl]
                    l += 1
                    sl += 1
        return ''.join(ans)
