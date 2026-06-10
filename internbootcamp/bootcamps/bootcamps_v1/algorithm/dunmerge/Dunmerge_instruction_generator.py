import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DunmergeInstructionGenerator(BaseInstructionGenerator):
    """Dunmerge Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dunmerge指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.params = {
            'min_n': params.get('min_n', 1),
            'max_n': params.get('max_n', 2000)
        }
    
    def case_generator(self):
        n = random.randint(self.params['min_n'], self.params['max_n'])
        all_elements = list(range(1, 2 * n + 1))
        random.shuffle(all_elements)
        a = all_elements[:n]
        b = all_elements[n:]
        random.shuffle(a)
        random.shuffle(b)
        p = self.merge(a, b)
        return {'n': n, 'p': p}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        p = question_case['p']
        p_str = ' '.join(map(str, p))
        prompt = f"""
        你有一个排列p，长度为2n，其中n={n}。p的具体值为：{p_str}。

        你需要判断是否存在两个长度为n的数组a和b，且它们的元素互不相同，使得p可以通过merge(a,b)过程得到。

        merge(a,b)的定义如下：
        - 如果其中一个数组为空，则结果是另一个数组。
        - 如果两个数组都不为空，比较a的第一个元素和b的第一个元素，较小的放在前面，然后递归处理剩下的部分。

        例如，a=[3,1]，b=[2,4]，则merge(a,b)=[2,3,1,4]。

        请判断是否存在这样的a和b，并将你的答案（YES或NO）放在[answer]标签中。

        请将答案以以下格式输出：
        [answer]
        YES或NO
        [/answer]
        """
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def merge(a, b):
        result = []
        i = j = 0
        while i < len(a) and j < len(b):
            if a[i] < b[j]:
                result.append(a[i])
                i += 1
            else:
                result.append(b[j])
                j += 1
        result.extend(a[i:])
        result.extend(b[j:])
        return result
