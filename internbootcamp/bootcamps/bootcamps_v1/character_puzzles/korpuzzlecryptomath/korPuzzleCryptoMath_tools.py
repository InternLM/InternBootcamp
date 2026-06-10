import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.korpuzzlecryptomath.korPuzzleCryptoMath_reward_calculator import KorpuzzlecryptomathRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorpuzzlecryptomathVerificationTool(BaseTool):
    """Korpuzzlecryptomath验证工具"""
    
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
            score = KorpuzzlecryptomathRewardCalculator.verify_score(
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
            logger.error(f"KorpuzzlecryptomathVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_equation(self):
        """动态生成有效等式"""
        # 生成随机加法结构：A + B + ... = SUM
        num_terms = random.randint(self.min_terms, self.max_terms)

        while True:
            # 生成随机数字组合
            digits = random.sample(range(0, 10), self.term_length)
            terms = [random.randint(10**(self.term_length-1), 10**self.term_length-1) 
                    for _ in range(num_terms)]
            total = sum(terms)

            if len(str(total)) == self.result_length:
                # 转换为字母模式
                letters = set()
                equation_parts = []
                for term in terms + [total]:
                    term_str = str(term)
                    if len(term_str) < self.term_length:
                        term_str = term_str.zfill(self.term_length)
                    equation_parts.append(term_str)
                    letters.update(term_str)

                # 确保结果首位非零
                if equation_parts[-1][0] == '0':
                    continue

                # 转换为字母方程
                char_map = {}
                unique_chars = list(letters)
                random.shuffle(unique_chars)
                for c in unique_chars:
                    char_map[c] = chr(65 + len(char_map))  # 映射到不同字母

                equation = []
                for part in equation_parts[:-1]:
                    equation.append(''.join([char_map[c] for c in part]))
                result = ''.join([char_map[c] for c in equation_parts[-1]])

                return f"{'+'.join(equation)}={result}"
