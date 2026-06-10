import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any




class CryoukosmemorynoteRewardCalculator(BaseRewardCalculator):
    """Cryoukosmemorynote奖励计算器"""
    
    @staticmethod
    def extract_output(output: str):
        """
        从模型输出中提取最后一个[answer]标签包裹的整数。
        """
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: int, identity: Dict[str, Any]) -> bool:
        """
        验证答案是否符合计算出的最小翻页数。
        """
        try:
            # 计算正确答案
            n = identity['n']
            m = identity['m']
            a = identity['a']
            correct = cls.compute_min_turns(n, m, a)
            return solution == correct
        except:
            return False
    
    # 其他额外方法

