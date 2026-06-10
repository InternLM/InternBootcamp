import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import List
from typing import Dict
from typing import Any




class BthreereligionsRewardCalculator(BaseRewardCalculator):
    """Bthreereligions奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> list:
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        if not answer_blocks:
            return None
        last_block = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_block.split('\n') if line.strip()]
        results = []
        for line in lines:
            line_upper = line.upper()
            if line_upper in ('YES', 'NO'):
                results.append(line_upper)
            else:
                return None
        return results if results else None
    
    @classmethod
    def _verify_correction(cls, solution: list, identity: dict) -> bool:
        expected = identity['expected_outputs']
        if not solution or len(solution) != len(expected):
            return False
        return all(s == e.upper() for s, e in zip(solution, expected))
    
    # 其他额外方法

