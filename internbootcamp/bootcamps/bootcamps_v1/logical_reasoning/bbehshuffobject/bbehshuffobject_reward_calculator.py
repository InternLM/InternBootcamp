import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import List
from typing import Dict
from typing import Tuple




class BbehshuffobjectRewardCalculator(BaseRewardCalculator):
    """Bbehshuffobject奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        matches = re.findall(r'<answer>(.*?)</answer>', output, re.DOTALL)
        # context_type = self.context_type
        # object_pools = self.object_pools[context_type]

        # output_lower = matches.lower()
        # print(f"out_l:{output_lower}")
        # for book in object_pools:
        #     if book.lower() in output_lower:
        #         return book.lower()
        # return None
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict) -> bool:
        # 注意：此处假设solution是通过extract_output(output, identity)获取的
        return solution.strip().lower() == identity["correct_answer"].strip().lower()
    
    # 其他额外方法

