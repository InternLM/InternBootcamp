import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class BbehobjectcountingInstructionGenerator(BaseInstructionGenerator):
    """Bbehobjectcounting Bootcamp指令生成器"""
    
    def __init__(self, categories=None, min_items=3, max_items=7, min_count=5, max_count=200, max_other_items=8, max_other_people=15):
        """
        初始化Bbehobjectcounting指令生成器
        
        Args:
            categories: 参数描述
            min_items: 参数描述
            max_items: 参数描述
            min_count: 参数描述
            max_count: 参数描述
            max_other_items: 参数描述
            max_other_people: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.categories = categories or [
            'fruits', 'animals/insects', 'cars', 
            'mobiles', 'musical instruments'
        ]
        self.min_items = min_items
        self.max_items = max_items
        self.min_count = min_count
        self.max_count = max_count
        self.max_other_items = max_other_items
        self.max_other_people = max_other_people
    
    def case_generator(self) -> Dict[str, Any]:
        # 确保选择不同的类别
        cat1, cat2 = random.sample(self.categories, 2)
        operation = random.choice(['sum', 'difference'])
        
        def generate_category(category: str) -> (List[str], int):
            item_count = random.randint(self.min_items, self.max_items)
            items = []
            total = 0
            for _ in range(item_count):
                num = random.randint(self.min_count, self.max_count)
                item = random.choice(self.category_vocab[category])
                story = self._generate_story(num)
                items.append(f"I have {num} {item} {story}.")
                total += num
            return items, total
        
        # 生成目标类别物品
        items1, sum1 = generate_category(cat1)
        items2, sum2 = generate_category(cat2)
        
        # 生成干扰物品（其他类别）
        other_items = []
        for cat in set(self.categories) - {cat1, cat2}:
            for _ in range(random.randint(0, self.max_other_items)):
                num = random.randint(1, self.max_count)
                item = random.choice(self.category_vocab[cat])
                other_items.append(f"I have {num} {item} {self._generate_story(num)}.")
                
        # 生成其他人物物品（至少5个）
        people_roles = ['grandmother', 'grandfather', 'mother', 'father',
                       'sister', 'brother', 'uncle', 'aunt', 'cousin', 'friend']
        other_people_items = []
        for _ in range(random.randint(self.max_other_people//2, self.max_other_people)):
            person = random.choice(people_roles)
            category = random.choice(self.categories)
            num = random.randint(1, 300)
            item = random.choice(self.category_vocab[category])
            other_people_items.append(f"My {person} has {num} {item}.")
        
        # 混合并打乱所有条目
        all_items = items1 + items2 + other_items + other_people_items
        random.shuffle(all_items)
        
        # 计算正确答案
        if operation == 'sum':
            answer = sum1 + sum2
        else:
            answer = abs(sum1 - sum2)
        
        return {
            'items': all_items,
            'categories': (cat1, cat2),
            'operation': operation,
            'correct_answer': answer,
            '_sums': (sum1, sum2)  # 用于调试
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        cat1, cat2 = question_case['categories']
        operation = question_case['operation']
        example1 = ', '.join(Bbehobjectcountingbootcamp.category_vocab[cat1][:3])
        example2 = ', '.join(Bbehobjectcountingbootcamp.category_vocab[cat2][:3])
        inventory_list = "\n".join(question_case['items'])
        operation_description = 'sum' if operation == 'sum' else 'absolute difference'
        
        return f"""You are an inventory analyst. Calculate the {operation} between my total {cat1} and {cat2} based on:

**Rules**
1. {cat1} include: {example1}, etc.
2. {cat2} include: {example2}, etc.

**Inventory List**
{inventory_list}

**Required Format**
Calculate the {operation_description} and put your final answer within [answer][/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_story(self, num: int) -> str:
        """生成数学正确的背景故事，包含至少三个步骤"""
        steps = random.choices(['gain', 'loss'], k=3)  # 确保三种操作
        current = num
        history = []

        # 逆向工程生成步骤
        for step in reversed(steps):
            if step == 'gain':
                delta = random.randint(1, max(10, current//2))
                history.insert(0, ('loss', delta))
                current += delta
            else:
                delta = random.randint(1, current-1) if current > 1 else 1
                history.insert(0, ('gain', delta))
                current -= delta

        # 构建故事
        parts = [f"initially I had {current}"]
        temp = current
        for action, value in history:
            if action == 'gain':
                temp += value
                parts.append(f"got {value} more")
            else:
                temp -= value
                parts.append(f"lost {value}")

        # 添加随机转折
        endings = [
            "but later found discrepancies",
            "after quality control checks",
            "due to unexpected circumstances",
            "following inventory adjustments"
        ]
        story = ', '.join(parts) + f", {random.choice(endings)} finally ending with {num}"
        return f"({story})"
