import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BbehobjectcountingVerificationTool(BaseTool):
    """Bbehobjectcounting验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = BbehobjectcountingRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"BbehobjectcountingVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
