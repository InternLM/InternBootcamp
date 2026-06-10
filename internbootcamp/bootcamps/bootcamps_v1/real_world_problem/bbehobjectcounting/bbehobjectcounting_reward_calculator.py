import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any
from typing import List
from typing import Dict
from typing import Any

# === 源文件中的全局函数 ===

def run_tests():
    # 初始化训练场对象
    bootcamp = Bbehobjectcountingbootcamp()

    print("Running tests for BbehObjectCountingbootcamp...\n")

    # 测试 _generate_story 方法
    print("Testing _generate_story...")
    num = 50
    story = bootcamp._generate_story(num)
    assert isinstance(story, str), "_generate_story should return a string"
    assert str(num) in story, "The final number should appear in the story"
    print("_generate_story passed.\n")

    # 测试 case_generator 方法
    print("Testing case_generator...")
    case = bootcamp.case_generator()
    assert 'items' in case, "case should contain 'items'"
    assert 'categories' in case, "case should contain 'categories'"
    assert 'operation' in case, "case should contain 'operation'"
    assert 'correct_answer' in case, "case should contain 'correct_answer'"

    assert isinstance(case['items'], list), "'items' should be a list"
    assert len(case['items']) > 0, "'items' should not be empty"

    cat1, cat2 = case['categories']
    assert cat1 in bootcamp.categories, f"{cat1} should be a valid category"
    assert cat2 in bootcamp.categories, f"{cat2} should be a valid category"
    assert cat1 != cat2, "Categories should be different"

    assert case['operation'] in ['sum', 'difference'], "Operation should be 'sum' or 'difference'"
    assert isinstance(case['correct_answer'], int), "Correct answer should be an integer"
    print("case_generator passed.\n")

    # 测试 prompt_func 方法
    print("Testing prompt_func...")
    prompt = bootcamp.prompt_func(case)
    assert isinstance(prompt, str), "prompt_func should return a string"
    assert '[answer]' in prompt, "Prompt should contain [answer] tag"
    assert case['categories'][0] in prompt, "Prompt should include the first category"
    assert case['categories'][1] in prompt, "Prompt should include the second category"
    print("prompt_func passed.\n")

    # 测试 extract_output 方法
    print("Testing extract_output...")
    output = "Some text [answer]1234[/answer] more text"
    extracted = bootcamp.extract_output(output)
    assert extracted == 1234, "extract_output should correctly extract the answer"

    output_with_comma = "Some text [answer]1,234[/answer] more text"
    extracted = bootcamp.extract_output(output_with_comma)
    assert extracted == 1234, "extract_output should handle commas"

    output_with_equals = "Some text [answer]result=1234[/answer] more text"
    extracted = bootcamp.extract_output(output_with_equals)
    assert extracted == 1234, "extract_output should handle equal signs"

    no_answer_output = "Some text without answer tags"
    extracted = bootcamp.extract_output(no_answer_output)
    assert extracted is None, "extract_output should return None when no answer is found"
    print("extract_output passed.\n")

    # 测试 _verify_correction 方法
    print("Testing _verify_correction...")
    correct_answer = case['correct_answer']
    assert bootcamp._verify_correction(correct_answer, case), "Correct answer should pass verification"

    wrong_answer = correct_answer + 1
    assert not bootcamp._verify_correction(wrong_answer, case), "Wrong answer should fail verification"
    print("_verify_correction passed.\n")

    print("All tests passed!")
    
    print(prompt)
    print("So, the correct answer is:", correct_answer, ".")


class BbehobjectcountingRewardCalculator(BaseRewardCalculator):
    """Bbehobjectcounting奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> int:
        # 处理多个可能的答案格式
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        # 提取最后一个答案并清洗格式
        raw_answer = matches[-1].strip().replace(',', '').replace(' ', '')
        # 处理可能的数学表达式
        if '=' in raw_answer:
            raw_answer = raw_answer.split('=')[-1]
        # 提取所有数字候选
        numbers = re.findall(r'-?\d+', raw_answer)
        return int(numbers[-1]) if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution: int, identity: Dict) -> bool:
        return solution == identity['correct_answer']
    
    # 其他额外方法

