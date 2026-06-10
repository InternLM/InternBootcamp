from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class BbehmultisteparithmeticInteraction(BaseInteraction):
    """Bbehmultisteparithmetic交互管理器"""
    
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
        score = BbehmultisteparithmeticRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个BbehMultistepArithmetic问题！"""
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
