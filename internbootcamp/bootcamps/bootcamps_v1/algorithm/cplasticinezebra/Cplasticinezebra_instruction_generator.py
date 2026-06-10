import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CplasticinezebraInstructionGenerator(BaseInstructionGenerator):
    """Cplasticinezebra Bootcamp指令生成器"""
    
    def __init__(self, min_length=1, max_length=20):
        """
        初始化Cplasticinezebra指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，支持生成长度1到20的测试案例
        """
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        """
        生成包含全交替、全同、混合模式的三类测试案例
        """
        pattern_type = random.choices(
            ['alternating', 'uniform', 'segmented'],
            weights=[0.3, 0.2, 0.5],  # 增加混合模式概率
            k=1
        )[0]

        length = random.randint(self.min_length, self.max_length)
        
        if pattern_type == 'alternating':
            start = random.choice(['b', 'w'])
            s = [start if i%2 == 0 else 'w' if start == 'b' else 'b' for i in range(length)]
        elif pattern_type == 'uniform':
            s = [random.choice(['b', 'w'])] * length
        else:
            # 生成分段交替模式（如 bbwwwbbww）
            s = []
            current = random.choice(['b', 'w'])
            while len(s) < length:
                # 随机生成1-3个相同字符
                seg_len = random.randint(1, 3)
                s.extend([current] * seg_len)
                current = 'w' if current == 'b' else 'b'
        
        s = ''.join(s[:length])
        return {'s': s}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        return f"""请根据以下规则解决斑马条纹问题：
1. 允许执行任意次数的分割反转操作（分割点任意选）
2. 每次操作将字符串分成左右两部分，分别反转后拼接
3. 目标是通过操作获得最长的连续交替颜色序列（相邻字符不同）

输入字符串：{s}

思考步骤：
1. 分析原始字符串的交替模式
2. 考虑如何通过分割反转合并不同的交替段
3. 特别注意字符串的循环特性可能带来的最长序列

将最终答案放在[answer]标签内，如：[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_max_zebra(s):
        """
        优化后的验证算法，处理边界情况
        """
        if not s:
            return 0

        max_len = current = 1
        doubled = s * 2

        # 遍历双倍字符串寻找最大交替序列
        for i in range(1, len(doubled)):
            if doubled[i] != doubled[i-1]:
                current += 1
                max_len = max(max_len, current)
            else:
                current = 1

        # 最终结果不能超过原字符串长度
        return min(max_len, len(s))
