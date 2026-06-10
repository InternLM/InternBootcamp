import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re
from copy import deepcopy




class BbehobjectpropertiesRewardCalculator(BaseRewardCalculator):
    """Bbehobjectproperties奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用非贪婪匹配查找所有答案块
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        # 提取最后一个答案块并清除前后空格
        return matches[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 直接比较提取答案和预先计算的正确答案
        try:
            return int(solution) == int(identity["correct_answer"])
        except:
            try:
                return solution.lower() == identity["correct_answer"].lower()
            except:
                return False
    
    # 其他额外方法

