import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import string




class CnamequestInstructionGenerator(BaseInstructionGenerator):
    """Cnamequest Bootcamp指令生成器"""
    
    def __init__(self, s_min_len=1, s_max_len=5, t_min_len=10, t_max_len=100):
        """
        初始化Cnamequest指令生成器
        
        Args:
            s_min_len: 参数描述
            s_max_len: 参数描述
            t_min_len: 参数描述
            t_max_len: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.s_min_len = s_min_len
        self.s_max_len = s_max_len
        self.t_min_len = max(t_min_len, 2)  # 确保至少可以分割
        self.t_max_len = t_max_len
    
    def case_generator(self):
        # 随机生成s
        s_len = random.randint(self.s_min_len, self.s_max_len)
        s = ''.join(random.choices(string.ascii_lowercase, k=s_len))
        
        # 控制有效性比例
        if random.random() < 0.5:
            t = self._generate_valid_t(s)
            # 随机插入噪声字符
            insert_pos = random.randint(0, len(t))
            noise = ''.join(random.choices(string.ascii_lowercase, 
                         k=random.randint(1,3)))
            t = t[:insert_pos] + noise + t[insert_pos:]
        else:
            t = self._generate_invalid_t(s)
        
        # 长度调整
        t = self._adjust_length(t)
        return {'s': s, 't': t}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        t = question_case['t']
        return f"""火星男孩需要将字符串t分割为左右两部分，每部分都包含s的子序列。字符串s是"{s}"，字符串t是"{t}"。请计算有效分割方式的数量，并将最终答案放在[answer]标签内。示例：[answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_t(self, s):
        """生成有效t字符串（保证s是t的子序列且存在分割点）"""
        # 生成左右部分各包含s的构造
        left = []
        ptr = 0
        for c in s:
            # 在字符前添加随机前缀
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            left.append(c)
            ptr += 1
        left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))

        right = []
        ptr = 0
        for c in s:
            # 在字符后添加随机后缀
            right.append(c)
            right.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            ptr += 1

        return (''.join(left) + ''.join(right)).replace('\x00', '')  # 防止空字符

    def _generate_invalid_t(self, s):
        """生成无效t字符串（保证至少有一半不满足条件）"""
        # 首先生成有效左半部分
        left = []
        ptr = 0
        for c in s:
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 2))))
            left.append(c)
        left = ''.join(left)

        # 生成无效右半部分（不包含s）
        right = ''.join(random.choices(string.ascii_lowercase, 
                      k=random.randint(len(s)+1, len(s)*2)))
        while self._is_subsequence(s, right):
            right = ''.join(random.choices(string.ascii_lowercase, 
                          k=random.randint(len(s)+1, len(s)*2)))

        return left + right

    def _is_subsequence(self, s, t):
        """正确实现子序列判断"""
        it = iter(t)
        return all(c in it for c in s)

    def _adjust_length(self, t):
        """确保t长度在合理范围内"""
        t = t[:self.t_max_len]
        while len(t) < self.t_min_len:
            t += random.choice(string.ascii_lowercase)
        return t
