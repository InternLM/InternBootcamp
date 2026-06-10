import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class KorciphercustominverseshiftsubstitutioncipherRewardCalculator(BaseRewardCalculator):
    """Korciphercustominverseshiftsubstitutioncipher奖励计算器"""
    
    @staticmethod
    def extract_output(text):
        """增强型答案提取"""
        import re
        # 匹配最后一个出现的[[...]]结构
        matches = re.findall(r'\[\[([A-Z]+)\]\]', text)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """通用验证逻辑"""
        return solution == identity['answer']
    
    # 其他额外方法

