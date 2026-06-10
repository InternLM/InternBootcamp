import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CyaroslavandalgorithmRewardCalculator(BaseRewardCalculator):
    """Cyaroslavandalgorithm奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        command_pattern = re.compile(r'^\S+?(>>|<>)\S+?$')
        valid_commands = []
        for line in lines:
            if command_pattern.fullmatch(line):
                valid_commands.append(line)
        return '\n'.join(valid_commands) if valid_commands else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        commands = []
        command_pattern = re.compile(r'^(\S+?)(>>|<>)(\S+?)$')
        lines = solution.strip().split('\n')
        if len(lines) > 50:
            return False
        for line in lines:
            line = line.strip()
            match = command_pattern.fullmatch(line)
            if not match:
                return False
            si, op, wi = match.groups()
            if len(si) > 7 or len(wi) > 7:
                return False
            commands.append((si, op, wi))
        for num in identity['numbers']:
            expected = cls.add_one(num)
            result, iterations = cls.apply_commands(num, commands)
            if iterations > 200 or result != expected:
                return False
        return True
    
    # 其他额外方法

