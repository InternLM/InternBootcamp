import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re




class CsequencetransformationInstructionGenerator(BaseInstructionGenerator):
    """Csequencetransformation Bootcamp指令生成器"""
    
    def __init__(self, n=None, min_n=1, max_n=10):
        """
        初始化Csequencetransformation指令生成器
        
        Args:
            n: 参数描述
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化谜题参数，可指定固定的n，或随机生成n的范围。

        参数:
            n (int, optional): 固定的n值。若提供，则生成的实例均为该n。
            min_n (int): 随机生成n时的最小值。
            max_n (int): 随机生成n时的最大值。
        """
        self.n = n
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """
        生成谜题实例，返回包含n值的字典。
        """
        import random
        if self.n is not None:
            return {'n': self.n}
        else:
            n = random.randint(self.min_n, self.max_n)
            return {'n': n}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将谜题实例转换为详细的文本问题，指导用户按指定格式回答。
        """
        n = question_case['n']
        prompt = f"""你是一个编程竞赛选手，需要解决以下问题：

给定一个初始序列1, 2, ..., {n}，通过以下过程生成结果序列：
1. 计算当前序列的GCD并添加到结果末尾。
2. 删除序列中的一个元素。
重复上述步骤直到序列为空，要求找到字典序最大的结果序列。

输入：n = {n}
输出：{n}个由空格分隔的整数，表示字典序最大的结果。

示例：
当n=3时，正确输出为：1 1 3，过程如下：
1. GCD(1,2,3)=1，删除2 → 剩余[1,3]
2. GCD(1,3)=1，删除1 → 剩余[3]
3. GCD(3)=3，删除3 → 结果[1,1,3]

请将答案放在[answer]标签内，例如：[answer]1 1 3[/answer]。
你的任务是解决n={n}的情况，并将最终答案按指定格式放置。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n):
        """
        递归生成字典序最大的结果序列。
        """
        if n == 1:
            return [1]
        elif n == 0:
            return []
        elif n == 3:
            return [1, 1, 3]
        res_length = (n + 1) // 2
        res = [1] * res_length
        remaining = n - res_length
        res2 = Csequencetransformationbootcamp.solve(remaining)
        res2_doubled = [x * 2 for x in res2]
        return res + res2_doubled
