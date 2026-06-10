import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re
from typing import Dict
from typing import Any
from typing import Optional
from collections import defaultdict
from collections import deque




class EjeremybearimyRewardCalculator(BaseRewardCalculator):
    """Ejeremybearimy奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[str]:
        """
        从模型输出中提取答案
        :param output: 模型输出的完整文本
        :return: 提取的答案字符串或None
        """
        match = re.search(r'\[answer\].*?G = (\d+), B = (\d+).*?\[/answer\]', output, re.DOTALL)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict[str, Any]) -> bool:
        """
        验证答案是否正确
        :param solution: 提取的答案字符串
        :param identity: 问题实例
        :return: 是否正确
        """
        try:
            G_str, B_str = solution.split()
            G = int(G_str)
            B = int(B_str)
            return G == identity['G'] and B == identity['B']
        except:
            return False
    
    # 其他额外方法

