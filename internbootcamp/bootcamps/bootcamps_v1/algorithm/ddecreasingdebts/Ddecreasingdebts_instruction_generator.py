import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re




class DdecreasingdebtsInstructionGenerator(BaseInstructionGenerator):
    """Ddecreasingdebts Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=5, min_m=0, max_m=10, d_min=1, d_max=100):
        """
        初始化Ddecreasingdebts指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            d_min: 参数描述
            d_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.d_min = d_min
        self.d_max = d_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        max_possible_m = min(self.max_m, 3 * n * (n-1))  # 允许每个(u,v)出现多次
        m = random.randint(self.min_m, max_possible_m)
        
        debts = []
        for _ in range(m):
            u = random.randint(1, n)
            v = random.randint(1, n)
            while u == v:
                v = random.randint(1, n)
            d = random.randint(self.d_min, self.d_max)
            debts.append([u, v, d])
        
        # 计算原始净债务数组
        original_net = [0] * (n + 1)
        for u, v, d in debts:
            original_net[u] += d
            original_net[v] -= d
        
        # 生成正确的solution
        positives = []
        negatives = []
        for i in range(1, n +1):
            if original_net[i] > 0:
                positives.append( (i, original_net[i]) )
            elif original_net[i] < 0:
                negatives.append( (i, original_net[i]) )
        
        result = []
        ptr_neg = 0
        for u_pos, remaining_pos in positives:
            while remaining_pos > 0 and ptr_neg < len(negatives):
                v_neg, remaining_neg = negatives[ptr_neg]
                transfer = min(remaining_pos, -remaining_neg)
                result.append( (u_pos, v_neg, transfer) )
                remaining_pos -= transfer
                # 更新负数债务的剩余量
                new_neg = remaining_neg + transfer
                if new_neg == 0:
                    ptr_neg += 1
                else:
                    negatives[ptr_neg] = (v_neg, new_neg)
        
        # 直接转换为最终结果（参考代码保证无重复）
        final_result = [[u, v, d] for u, v, d in result]
        
        identity = {
            'input': {
                'n': n,
                'm': m,
                'debts': debts
            },
            'original_net': original_net,
            'expected_total': sum(val for val in original_net if val > 0)
        }
        return identity
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['input']['n']
        m = question_case['input']['m']
        debts = question_case['input']['debts']
        debts_desc = "\n".join([f"{u} {v} {d}" for u, v, d in debts])
        prompt = f"""你是债务合并专家，需要根据以下规则将债务合并以使总债务最小化：

规则说明：
1. 债务转移：若存在两笔债务d(a,b) >0 和 d(c,d) >0（其中a≠c或b≠d），可以选择减少这两笔债务z（z为两者中的较小值），同时增加d(c,b)和d(a,d)各z。
2. 消除自环债务：若某人有自环债务d(a,a) >0，可将其置零。

输入数据：
- 第1行：两个整数n（人数）和m（初始债务数量）
- 接下来m行：每行三个整数u, v, d，表示u欠v共d burles

任务：
应用上述规则，输出处理后的债务，使得总债务最小。输出格式为：
- 第1行：剩余债务数量m'
- 随后m'行：每行三个整数u, v, d，表示u欠v的最终债务d

当前问题：
n = {n}, m = {m}
债务列表：
{debts_desc}

请按照上述格式要求，将最终答案严格按以下格式放置在[answer]和[/answer]之间：
[answer]
m'
u1 v1 d1
u2 v2 d2
...
[/answer]

确保：
1. 每个(u,v)对唯一且u≠v，d>0
2. 所有数值为普通整数（无科学计数法）"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

