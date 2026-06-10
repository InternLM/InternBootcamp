import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random




class CfirstdigitlawInstructionGenerator(BaseInstructionGenerator):
    """Cfirstdigitlaw Bootcamp指令生成器"""
    
    def __init__(self, max_N=10, **params):
        """
        初始化Cfirstdigitlaw指令生成器
        
        Args:
            max_N: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_N = max_N  # 控制问题规模以便测试
    
    def case_generator(self):
        N = random.randint(1, self.max_N)
        variables = []
        for _ in range(N):
            # 生成更丰富的数值区间分布
            if random.random() < 0.3:
                # 特殊形式：生成以1开头的大范围数值
                exp = random.randint(0, 17)
                Li = 10**exp
                Ri = 10**exp * 2 - 1
            else:
                # 通用生成逻辑
                exp = random.randint(0, 18)
                Li = random.randint(10**exp // 10, 10**exp - 1) if exp > 0 else 1
                max_exp_ri = random.randint(exp, 18)
                max_ri = min(10**max_exp_ri - 1, 10**18)
                Ri = random.randint(Li, max_ri)
            
            variables.append({"L": Li, "R": Ri})
        
        K = random.randint(0, 100)
        return {
            "N": N,
            "variables": variables,
            "K": K
        }
    
    @staticmethod
    def prompt_func(question_case):
        N = question_case['N']
        variables = question_case['variables']
        K = question_case['K']
        required_num = (N * K + 99) // 100
        
        problem = f"""根据本福特定律研究问题，请计算{N}个独立随机变量满足条件的概率：

每个变量的取值范围如下："""
        for idx, var in enumerate(variables, 1):
            problem += f"\n变量{idx}: [{var['L']}, {var['R']}]，其中每个整数等概率出现"
        
        problem += f"""
要求计算至少{required_num}个变量的最高位为1的概率（即至少达到{K}%的比例）。

请输出精确到小数点后15位的概率值，并确保绝对/相对误差≤1e-9。答案请用[answer]和[/answer]标签包裹。

示例：
[answer]0.123456789012345[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

