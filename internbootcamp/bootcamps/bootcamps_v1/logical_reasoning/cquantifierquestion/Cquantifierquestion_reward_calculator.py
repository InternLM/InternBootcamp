import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CquantifierquestionRewardCalculator(BaseRewardCalculator):
    """Cquantifierquestion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个答案块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        content = answer_blocks[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        # 处理-1的情况
        if lines[0] == '-1':
            return -1
        # 尝试解析两行格式
        if len(lines) >= 2:
            count_line = lines[0]
            quant_line = lines[1].upper()
            if count_line.isdigit() and len(quant_line) == int(count_line) and all(c in 'AE' for c in quant_line):
                return (int(count_line), quant_line)
        # 尝试单行格式，例如 "1 EA"
        if len(lines) == 1:
            parts = lines[0].split()
            if len(parts) == 2 and parts[0].isdigit() and len(parts[1]) == int(parts[0]):
                quant = parts[1].upper()
                if all(c in 'AE' for c in quant):
                    return (int(parts[0]), quant)
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 获取参考解
        ref_sol = cls.reference_solution(identity)
        # 处理无解情况
        if isinstance(ref_sol, int):
            return solution == -1
        # 处理有解情况
        return solution == ref_sol
    
    # 其他额外方法

