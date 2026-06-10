import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import random
import re




class BbornthiswayInstructionGenerator(BaseInstructionGenerator):
    """Bbornthisway Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bbornthisway指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        default_params = {
            'n_min': 1,
            'n_max': 5,
            'm_min': 1,
            'm_max': 5,
            'ta_min': 1,
            'ta_max': 100,
            'tb_min': 1,
            'tb_max': 100,
            'k_min': 1,
            'k_max': None,
        }
        self.params = default_params.copy()
        self.params.update(params)
    
    def case_generator(self):
        n = random.randint(self.params['n_min'], self.params['n_max'])
        m = random.randint(self.params['m_min'], self.params['m_max'])
        ta = random.randint(self.params['ta_min'], self.params['ta_max'])
        tb = random.randint(self.params['tb_min'], self.params['tb_max'])
        max_k = n + m

        # Handle k constraints
        k_min = max(1, self.params['k_min'])
        k_min = min(k_min, max_k)  # Ensure within valid range
        
        k_max_param = self.params['k_max']
        if k_max_param is None:
            effective_k_max = max_k
        else:
            effective_k_max = min(k_max_param, max_k)
        
        effective_k_max = max(k_min, effective_k_max)
        effective_k_max = min(effective_k_max, max_k)  # Final validation
        
        k = random.randint(k_min, effective_k_max) if effective_k_max >= k_min else k_min

        # Generate strictly increasing flight times
        a = sorted(random.sample(range(1, 1000), n))
        b = sorted(random.sample(range(1, 1000), m))

        return {
            'n': n, 'm': m, 'ta': ta, 'tb': tb, 'k': k,
            'a': a, 'b': b
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a_str = ', '.join(map(str, question_case['a']))
        b_str = ', '.join(map(str, question_case['b']))
        prompt = f"""航空调度谜题：
- 从A到B有{question_case['n']}个航班（出发时间：{a_str}，飞行耗时{question_case['ta']}）
- 从B到C有{question_case['m']}个航班（出发时间：{b_str}，飞行耗时{question_case['tb']}）
- 你可取消最多{question_case['k']}个航班

规则：
1. 能转机的条件：B出发时间 ≥ A航班到达时间（A出发+{question_case['ta']}）
2. 你的目标是让Arkady最晚到达C
3. 若无法到达输出-1

请计算最优解，并将最终答案用[answer]包裹。例如：[answer]11[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

