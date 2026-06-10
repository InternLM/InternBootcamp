from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.cryptomath_reward_calculator import CryptomathRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.lib.crypto_math import generate_crypto_math




class CryptomathInteraction(BaseInteraction):
    """Cryptomath交互管理器"""
    
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
        score = CryptomathRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个cryptomath问题！"""
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
    def generator(self):
        results = generate_crypto_math(self.num_letters, 1, self.num_add)
        puzzle = results[0]["puzzle"]
        self.puzzle = puzzle
        return self.puzzle

    def get_question(self):
        statements = [f"""你是一个专门解决定制谜题问题的智能助手。请准确应用下面的规则解答题目。

谜题规则：
给出一个字母公式，每个字母代表一个唯一数字（0-9）。不同字母不能代表相同数字，任何多位数的首字母不能为 0。

问题：
{self.puzzle}

请以字母=数字的形式给出答案，并将最终答案用双括号括起来，例如：[[A=1,B=2,...]]。

答案："""]

        return random.choice(statements)


    def get_question_following(self):
        followings = []
        followings.append("""\n
    等于数字的形式给出你的答案，并且把答案放在双括号内，比如这样：[[A=1,B=2,...]]。""")
        return random.choice(followings)

    @staticmethod
    def parse_question(question: str) -> dict:
        pattern = r'(?:问题|题目|输入算式为|问题是)[：:]\s*([A-Z+]+=[A-Z]+)'
        match = re.search(pattern, question)
        if not match:
            return None
        equation = match.group(1)
        left, right = equation.split('=')
        terms = left.split('+')
        leading_letters = set()
        letters = set()
        for term in terms + [right]:
            letters.update(term)
            if len(term) > 1:
                leading_letters.add(term[0])
        return {
            'left_terms': terms,
            'right_term': right,
            'leading_letters': list(leading_letters),
            'all_letters': list(letters)
        }

    @staticmethod
    def check_solution(parsed_question: dict, parsed_response: dict) -> bool:
        def has_solution(pq):
            letters = list(pq['all_letters'])
            leading = pq['leading_letters']
            n = len(letters)
            for perm in permutations(range(10), n):
                assignment = dict(zip(letters, perm))
                valid = all(assignment[l] != 0 for l in leading)
                if not valid:
                    continue
                left_sum = 0
                for term in pq['left_terms']:
                    num = 0
                    for c in term:
                        num = num * 10 + assignment[c]
                    left_sum += num
                right_num = 0
                for c in pq['right_term']:
                    right_num = right_num * 10 + assignment[c]
                if left_sum == right_num:
                    return True
            return False

        if parsed_response is None:
            return not has_solution(parsed_question)
        else:
            pq = parsed_question
            resp = parsed_response
            leading = pq['leading_letters']
            for letter in leading:
                if resp.get(letter, 0) == 0:
                    return False
            values = list(resp.values())
            if len(values) != len(set(values)):
                return False
            if set(resp.keys()) != set(pq['all_letters']):
                return False
            left_sum = 0
            for term in pq['left_terms']:
                num = 0
                for c in term:
                    num = num * 10 + resp[c]
                left_sum += num
            right_num = 0
            for c in pq['right_term']:
                right_num = right_num * 10 + resp[c]
            return left_sum == right_num
