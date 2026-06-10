import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehmultisteparithmetic.BbehMultistepArithmetic_reward_calculator import BbehmultisteparithmeticRewardCalculator

# 导入依赖库
import logging
import re
import time
from typing import Dict
from typing import Any
from typing import Optional
from typing import Union
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehmultisteparithmetic.lib.bbeh_multistep_arithmetic.bbeh_arithmetic_generator import BBEHArithmeticGenerator
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehmultisteparithmetic.lib.bbeh_multistep_arithmetic.bbeh_arithmetic_solver import BBEHArithmeticSolver
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bbehmultisteparithmetic.lib.bbeh_multistep_arithmetic.bbeh_arithmetic_validor import BBEHArithmeticVerifier

# === 源文件中的全局函数 ===

def print_section(title: str, char: str = "=") -> None:
    """打印带有分隔线的章节标题"""
    width = 80
    print(f"\n{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}\n")

def format_statistics(stats: Dict) -> str:
    """格式化统计信息"""
    output = []
    output.append("总体统计:")
    output.append(f"  总测试案例: {stats['total_cases']}")
    output.append(f"  正确答案数: {stats['correct_answers']}")
    output.append(f"  总体成功率: {stats['success_rate']}%")

    output.append("\n按难度分类:")
    for diff in ['easy', 'medium', 'hard']:
        diff_stats = stats['by_difficulty'][diff]
        output.append(
            f"  {diff.capitalize()}: {diff_stats['correct']}/{diff_stats['total']} ({diff_stats['success_rate']})")

    output.append("\n按表达式长度分类:")
    for length in ['short', 'medium', 'long']:
        length_stats = stats['by_expression_length'][length]
        output.append(
            f"  {length.capitalize()}: {length_stats['correct']}/{length_stats['total']} ({length_stats['success_rate']})")

    output.append("\n运算符使用统计:")
    for op, op_stats in stats['by_operator'].items():
        output.append(f"  {op}: {op_stats['correct']}/{op_stats['total']} ({op_stats['success_rate']})")

    return "\n".join(output)

def format_statistics(stats: Dict) -> str:
    """格式化统计信息"""
    output = []
    output.append("总体统计:")
    output.append(f"  总测试案例: {stats['total_cases']}")
    output.append(f"  正确答案数: {stats['correct_answers']}")
    output.append(f"  总体成功率: {stats['success_rate']}%")

    output.append("\n按难度分类:")
    for diff in ['easy', 'medium', 'hard']:
        diff_stats = stats['by_difficulty'][diff]
        output.append(
            f"  {diff.capitalize()}: {diff_stats['correct']}/{diff_stats['total']} ({diff_stats['success_rate']})")

    output.append("\n按表达式长度分类:")
    for length in ['short', 'medium', 'long']:
        length_stats = stats['by_expression_length'][length]
        output.append(
            f"  {length.capitalize()}: {length_stats['correct']}/{length_stats['total']} ({length_stats['success_rate']})")

    output.append("\n运算符使用统计:")
    for op, op_stats in stats['by_operator'].items():
        output.append(f"  {op}: {op_stats['correct']}/{op_stats['total']} ({op_stats['success_rate']})")

    return "\n".join(output)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BbehmultisteparithmeticVerificationTool(BaseTool):
    """Bbehmultisteparithmetic验证工具"""
    
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
            score = BbehmultisteparithmeticRewardCalculator.verify_score(
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
            logger.error(f"BbehmultisteparithmeticVerificationTool执行错误: {str(e)}")
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
    def _generate_fallback_case(self) -> Dict:
        """生成一个简单的后备案例"""
        expression = "(2 + 3) * 4"  # 简单且保证可解的表达式
        answer = 20.0

        return {
            "expression": expression,
            "answer": answer,
            "solution": answer,
            "difficulty": "easy",
            "language": self.language,
            "is_fallback": True
        }

    def _count_operators(self, expression: str) -> Dict[str, int]:
        """统计表达式中的运算符使用情况"""
        operators = {
            '+': 0, '-': 0, '*': 0, '/': 0, '><': 0, ';': 0,
            '@': 0, '<>': 0, '[]': 0, '#': 0, '!': 0, '~': 0,
            '&': 0, ':': 0, '][': 0
        }

        i = 0
        while i < len(expression):
            # 检查两字符运算符
            if i + 1 < len(expression):
                two_char = expression[i:i + 2]
                if two_char in operators:
                    operators[two_char] += 1
                    i += 2
                    continue

            # 检查单字符运算符
            if expression[i] in operators:
                operators[expression[i]] += 1

            i += 1

        return {op: count for op, count in operators.items() if count > 0}

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.verifier.get_statistics()

    def reset_statistics(self) -> None:
        """重置统计信息"""
        self.verifier.reset_statistics()

    def set_language(self, language: str) -> None:
        """设置语言"""
        if language in ["en", "zh"]:
            self.language = language
        else:
            raise ValueError("不支持的语言。请使用 'en' 或 'zh'。")

    def set_difficulty(self, difficulty: str) -> None:
        """设置难度级别"""
        if difficulty in ["easy", "medium", "hard"]:
            self.difficulty = difficulty
        else:
            raise ValueError("不支持的难度级别。请使用 'easy', 'medium', 或 'hard'。")

    def set_timeout(self, timeout: int) -> None:
        """设置超时时间"""
        if timeout > 0:
            self.timeout = timeout
        else:
            raise ValueError("超时时间必须为正数。")
