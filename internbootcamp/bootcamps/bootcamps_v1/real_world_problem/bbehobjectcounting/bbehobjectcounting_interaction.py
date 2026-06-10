from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.real_world_problem.bbehobjectcounting.bbehobjectcounting_reward_calculator import BbehobjectcountingRewardCalculator

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


class BbehobjectcountingInteraction(BaseInteraction):
    """Bbehobjectcounting交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = BbehobjectcountingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个bbehobjectcounting问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法
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
