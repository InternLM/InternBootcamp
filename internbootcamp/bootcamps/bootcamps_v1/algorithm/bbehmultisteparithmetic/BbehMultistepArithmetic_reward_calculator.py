import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class BbehmultisteparithmeticRewardCalculator(BaseRewardCalculator):
    """Bbehmultisteparithmetic奖励计算器"""
    
    @classmethod
    def extract_output(cls, output: str) -> Optional[float]:
        """从输出中提取答案"""
        try:
            # 查找Python代码块
            pattern = r"```json\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*```"
            match = re.search(pattern, output)
            if not match:
                # 尝试查找任何数字
                pattern = r"Final-answer:.*?([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)"
                match = re.search(pattern, output)
                if not match:
                    return None

            # 转换为浮点数
            return float(match.group(1))

        except (ValueError, AttributeError) as e:
            return None
    
    @classmethod
    def _verify_correction(cls, output: int, identity: Dict) -> float:
        """验证答案并评分"""
        try:
            if output is None:
                # print("❌ 错误: 无法从输出中提取答案")
                return 0.0

            # 验证答案
            # expected_answer = identity.get('solution', identity.get('answer'))
            is_correct = cls.verifier.verify_answer(identity, output)

            return is_correct
        except Exception as e:
            # print(f"❌ 错误: 验证过程中出现异常: {str(e)}")
            return 0.0
    
    # 其他额外方法

