import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.cryptomath_reward_calculator import CryptomathRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cryptomath.lib.crypto_math import generate_crypto_math



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CryptomathVerificationTool(BaseTool):
    """Cryptomath验证工具"""
    
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
            score = CryptomathRewardCalculator.verify_score(
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
            logger.error(f"CryptomathVerificationTool执行错误: {str(e)}")
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
