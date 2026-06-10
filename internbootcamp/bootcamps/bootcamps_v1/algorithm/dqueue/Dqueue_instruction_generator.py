import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DqueueInstructionGenerator(BaseInstructionGenerator):
    """Dqueue Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, ti_min=1, ti_max=1000):
        """
        初始化Dqueue指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            ti_min: 参数描述
            ti_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_n = min_n
        self.max_n = max_n
        self.ti_min = ti_min
        self.ti_max = ti_max  # Adjusted default to avoid range errors
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        ti = [random.randint(self.ti_min, self.ti_max) for _ in range(n)]
        return {'n': n, 'ti': ti}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        ti_str = ' '.join(map(str, question_case['ti']))
        prompt = f"""你是一位排队优化专家，请帮助Susie找出调整队列顺序后可以得到的最大不失望人数。规则如下：

队列中有n个人，每个人有一个服务时间ti。当一个人等待的时间（即他前面所有人的服务时间总和）超过他的ti时，他会感到失望。我们的目标是通过调整队列顺序，使得不失望的人数最大化。请根据下面的输入数据，计算正确的答案，并按照指定格式返回结果。

输入格式：
第一行是一个整数n，表示人数。
第二行包含n个整数，表示每个人的服务时间ti，用空格分隔。

请仔细阅读输入数据，并输出最大可能的不失望人数，将结果放在[answer]和[/answer]标签之间。

示例输入：
5
15 2 1 5 3

示例输出：
[answer]4[/answer]

现在，根据以下输入数据，给出你的解答：

输入：
{n}
{ti_str}

请确保答案的格式正确，并将最终结果放置在[answer]标签中。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

