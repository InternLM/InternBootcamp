import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CrussianrouletteInstructionGenerator(BaseInstructionGenerator):
    """Crussianroulette Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Crussianroulette指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(1, params.get('n_min', 1))
        self.n_max = max(self.n_min, params.get('n_max', 20))
        self.k_min = max(0, params.get('k_min', 0))
        self.k_max = params.get('k_max')
        self.p_min = max(1, params.get('p_min', 1))
        self.p_max = max(self.p_min, params.get('p_max', 5))
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k_upper = min(n, self.k_max) if self.k_max is not None else n
        k = random.randint(max(self.k_min, 0), k_upper)
        p = random.randint(self.p_min, self.p_max)
        # 生成可能包含重复的查询位置
        queries = [random.randint(1, n) for _ in range(p)]  
        return {'n': n, 'k': k, 'queries': queries}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""作为转轮手枪专家，请解决以下配置问题：

# 基础参数
- 总槽位：{question_case['n']}
- 子弹数：{question_case['k']}
- 需查询的槽位位置：{question_case['queries']}

# 配置要求
1. 找到最小化Sasha死亡概率的配置方案
2. 当存在多个最优方案时选择字典序最小的（'.' < 'X'）

# 转轮运作规则
- 每次射击后若无子弹，转轮左移1位
- 射击顺序：Sasha -> Roma -> Sasha... 交替进行

# 输出格式
将最终答案用[answer][/answer]包裹，例如查询位置2和5时为：[answer].X[/answer]

请严格按照要求输出：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

