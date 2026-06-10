import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CokabeandboxesInstructionGenerator(BaseInstructionGenerator):
    """Cokabeandboxes Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Cokabeandboxes指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """初始化参数，允许配置生成的盒子数量范围"""
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """生成一个合法的命令序列，包含交替的add和remove操作"""
        n = random.randint(self.min_n, self.max_n)
        add_order = list(range(1, n+1))
        random.shuffle(add_order)  # 随机生成添加顺序
        
        stack = []
        commands = []
        add_count = 0
        remove_count = 0
        expected_i = 1  # 当前期望移除的盒子编号
        
        while add_count < n or remove_count < n:
            # 优先添加未添加的盒子，但在适当条件下允许remove
            can_add = add_count < n
            can_remove = remove_count < add_count and expected_i <= n
            
            if can_add and (not can_remove or random.random() < 0.5):
                x = add_order[add_count]
                commands.append(f'add {x}')
                stack.append(x)
                add_count += 1
            else:
                commands.append('remove')
                # 即使栈顶不是期望的i也强制移除（模拟问题中的不可行操作）
                if stack and stack[-1] == expected_i:
                    stack.pop()
                expected_i += 1
                remove_count += 1
        
        # 计算正确答案
        expected_ans = self._compute_ans(n, commands)
        return {
            'n': n,
            'commands': commands,
            'expected_ans': expected_ans
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """构造包含详细规则描述和示例的问题文本"""
        n = question_case['n']
        commands = '\n'.join(question_case['commands'])
        prompt = (
            "你是Daru，需要处理Okabe的指令来添加和移除盒子。当无法直接移除时，你可以重新排序栈。\n\n"
            "规则：\n"
            "1. 初始栈为空，共有n（n={}）个盒子，编号1~{}。\n"
            "2. 你会收到2n条命令：'add x'将x添加到栈顶，'remove'移除栈顶盒子。\n"
            "3. 需要确保最终移除顺序为1,2,...,n。若无法直接移除，可任选时机重排栈。\n"
            "4. 求最少需要重排的次数。\n\n"
            "输入格式：\n"
            "首行为n，随后2n行每行为命令。\n\n"
            "输入示例：\n{}\n\n"
            "请输出答案，并用[answer]和[/answer]标签包裹。例如：[answer]2[/answer]。"
        ).format(n, n, f"{n}\n{commands}")
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_ans(n, commands):
        """根据输入命令计算最小重排次数（参考原题解逻辑）"""
        stack = []
        ans = p = stack_length = 0
        current_expected = 1
        for cmd in commands:
            if cmd.startswith('remove'):
                if stack_length > p and (stack and stack[-1] != current_expected):
                    ans += 1
                    p = stack_length
                if stack:
                    stack.pop()
                stack_length -= 1
                if p > stack_length:
                    p = stack_length
                current_expected += 1
            else:
                x = int(cmd.split()[1])
                stack.append(x)
                stack_length += 1
        return ans
