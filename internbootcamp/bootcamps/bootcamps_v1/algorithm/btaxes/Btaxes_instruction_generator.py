import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BtaxesInstructionGenerator(BaseInstructionGenerator):
    """Btaxes Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10**9):
        """
        初始化Btaxes指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数校验优化，支持更大范围的n值生成
        """
        if n_min < 2:
            raise ValueError("n_min must be ≥2")
        if n_max < n_min:
            raise ValueError("n_max must be ≥n_min")

        self.n_min = n_min
        self.n_max = n_max
    
    def case_generator(self):
        """主动构造四类典型案例，保证覆盖率"""
        def is_prime(m):
            if m <= 1:
                return False
            if m <=3:
                return True
            if m % 2 ==0 or m %3 ==0:
                return False
            i = 5
            w = 2
            while i*i <= m:
                if m%i ==0:
                    return False
                i += w
                w = 6 - w
            return True
        
        # 主动生成四类案例的平衡策略
        case_type = random.choice([
            'prime',         # 质数案例
            'even_composite',# 偶合数
            'odd_case2',     # 奇合数(n-2是质数)
            'odd_case3'      # 奇合数(n-2是合数)
        ])
        
        max_attempts = 1000
        for _ in range(max_attempts):
            # 动态调整生成策略
            if case_type == 'prime':
                # 生成随机质数
                n = random.randint(max(2, self.n_min), self.n_max)
                if is_prime(n):
                    return {'n': n, 'correct_answer': 1}
                
            elif case_type == 'even_composite':
                # 生成至少有两个质因子的偶数
                n = 2 * random.randint(2, self.n_max//2)
                if n >= 2 and not is_prime(n):
                    return {'n': n, 'correct_answer': 2}
            
            elif case_type == 'odd_case2':
                # 生成奇合数并满足n-2是质数
                base_prime = random.choice([3,5,7,11,13,17,19,23,29,31])
                n = base_prime + 2
                if n % 2 == 1 and not is_prime(n) and is_prime(base_prime):
                    return {'n': n, 'correct_answer': 2}
                # 动态生成
                candidate = random.randint(max(3, self.n_min), self.n_max)
                if candidate%2 ==1 and not is_prime(candidate) and is_prime(candidate-2):
                    return {'n': candidate, 'correct_answer': 2}
            
            elif case_type == 'odd_case3':
                # 确保生成正确结果为3的案例
                candidates = [27, 35, 45, 49, 55, 81, 875, 12345]
                for n in candidates:
                    if self.n_min <= n <= self.n_max:
                        if not is_prime(n) and n%2 ==1 and not is_prime(n-2):
                            return {'n': n, 'correct_answer': 3}
                # 动态生成
                candidate = random.randint(max(9, self.n_min), self.n_max)
                if candidate%2 ==1 and not is_prime(candidate) and not is_prime(candidate-2):
                    return {'n': candidate, 'correct_answer': 3}
        
        # Fallback机制：确保至少返回有效案例
        return {'n': 4, 'correct_answer': 2}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        return f"""根据俄罗斯税法规定，Funt先生的年收入为{n} burles，需要通过分割收入来最小化税款。规则如下：

1. 将总金额分割为k个整数（k≥1），每个部分≥2
2. 每个部分的税款为其最大真因子（即除自身外的最大约数）
3. 最终税款为各部分税款之和

请计算最小可能的税款金额，并将最终答案置于[answer]标签内，如：[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

