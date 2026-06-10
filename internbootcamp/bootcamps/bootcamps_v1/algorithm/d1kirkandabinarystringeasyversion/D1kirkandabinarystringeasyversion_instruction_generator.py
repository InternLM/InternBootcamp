import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class D1kirkandabinarystringeasyversionInstructionGenerator(BaseInstructionGenerator):
    """D1kirkandabinarystringeasyversion Bootcamp指令生成器"""
    
    def __init__(self, min_length=3, max_length=2000):
        """
        初始化D1kirkandabinarystringeasyversion指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，设置生成字符串的最小和最大长度。
        添加特殊场景生成概率参数，增强测试覆盖率
        """
        self.min_length = min_length
        self.max_length = max_length
        self.special_case_prob = 0.3  # 30%概率生成特殊场景案例
    
    def case_generator(self):
        """
        生成二进制字符串s，包含随机、全0、全1、交替模式等多种场景
        根据算法生成对应的正确解t
        """
        n = random.randint(self.min_length, self.max_length)
        
        # 30%概率生成特殊模式字符串
        if random.random() < self.special_case_prob:
            pattern = random.choice(['all_zero', 'all_one', 'alternate'])
            if pattern == 'all_zero':
                s = '0' * n
            elif pattern == 'all_one':
                s = '1' * n
            else:  # alternate模式
                s = ('01' * (n//2 + 1))[:n]
        else:
            s = ''.join(random.choices(['0', '1'], k=n))
        
        t = self.compute_t(s)
        return {"s": s, "t": t}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        增强问题描述的规则说明，补充边界条件说明
        """
        s = question_case['s']
        prompt = f"""你是一个二进制字符串处理专家，请解决以下问题：

给定一个二进制字符串s，构造一个新的二进制字符串t，满足下列条件：
1. 对于所有可能的子区间[l, r] (1 ≤ l ≤ r ≤ n)，s的子串s[l..r]的最长非递减子序列(LNDS)长度必须严格等于t对应子串t[l..r]的LNDS长度
2. 在满足条件1的前提下，t中0的数量要尽可能多

附加规则说明：
- 子序列不需要连续，但元素必须保持原始顺序
- 当s全为0时，t必须等于s（此时已是最优解）
- 当s全为1时，t可以是全0（观察示例验证此情况）
- 对于形如"01"交替的字符串，需要确保每个1的位置被正确处理

输入s为：{s}

你的输出必须是长度与s相同（{len(s)}位）的二进制字符串。请将最终答案放在[answer]和[/answer]标签之间，例如：[answer]010[/answer]。答案必须完全匹配正则表达式：^[01]+$"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_t(s_str):
        """
        根据参考算法计算给定二进制字符串s的正确解t。
        添加类型转换确保处理字节型数据
        """
        s = list(map(int, s_str))
        n = len(s)
        t = [0] * n
        stack = []
        for i in range(n):
            if s[i] == 1:
                stack.append(i)
            else:
                if stack:
                    idx = stack.pop()
                    t[idx] = 1
        return ''.join(map(str, t))
