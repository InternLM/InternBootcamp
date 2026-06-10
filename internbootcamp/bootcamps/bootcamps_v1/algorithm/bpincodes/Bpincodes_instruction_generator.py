import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import string
import random
import itertools




class BpincodesInstructionGenerator(BaseInstructionGenerator):
    """Bpincodes Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10):
        """
        初始化Bpincodes指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        original_pins = []
        attempts = 0
        
        # 生成具有可控重复程度的初始PIN码
        while len(original_pins) < n:
            # 保证至少有1个重复项以触发修改逻辑
            if len(original_pins) == 0 or (len(original_pins) >= 1 and attempts < 10):
                pin = ''.join(random.choices(string.digits, k=4))
                original_pins.append(pin)
                attempts += 1
            else:  # 添加重复项
                original_pins.append(random.choice(original_pins))
        
        # 使用确定性算法生成解决方案
        expected_k, modified_pins = self.solve_puzzle(original_pins)
        
        return {
            'n': n,
            'original_pins': original_pins,
            'expected_k': expected_k,
            'expected_pins': modified_pins  # 增加预期结果存储
        }
    
    @staticmethod
    def prompt_func(question_case):
        original_pins = question_case['original_pins']
        n = question_case['n']
        example = "\n".join(original_pins)
        return f"""Polycarp的{n}个原始PIN码：
{example}

要求：
1. 修改最少位数使所有PIN唯一
2. 保持原始顺序
3. 输出格式：
[answer]
k
new_pin1
...
new_pin{n}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_puzzle(pins):
        unique_set = set()
        modified = []
        changes = 0

        for idx, pin in enumerate(pins):
            if pin not in unique_set:
                modified.append(pin)
                unique_set.add(pin)
                continue

            # 生成所有可能的一位修改候选
            candidates = []
            for pos in range(4):
                for digit in string.digits:
                    if digit == pin[pos]:
                        continue
                    candidate = pin[:pos] + digit + pin[pos+1:]
                    if candidate not in unique_set and candidate not in pins[idx+1:]:
                        candidates.append(candidate)

            # 选择最早不冲突的候选
            for candidate in candidates:
                if candidate not in unique_set:
                    modified.append(candidate)
                    unique_set.add(candidate)
                    changes += 1
                    break
            else:
                # 回退机制：生成全新PIN
                for _ in range(1000):
                    new_pin = ''.join(random.choices(string.digits, k=4))
                    if new_pin not in unique_set and new_pin not in pins[idx+1:]:
                        modified.append(new_pin)
                        unique_set.add(new_pin)
                        changes += 1
                        break
                else:
                    raise RuntimeError("Failed to find solution")

        # 验证解决方案有效性
        assert len(modified) == len(pins), "Length mismatch"
        assert len(set(modified)) == len(pins), "Duplicate found"
        return changes, modified
