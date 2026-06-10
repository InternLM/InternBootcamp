import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import ast
import re
import ast
import random

# === 源文件中的全局变量 ===

BLOOD_TEST_REFERENCE = {
    "白细胞计数": {
        "abbr": "WBC",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (3.5, 9.5)
    },
    "红细胞计数": {
        "abbr": "RBC",
        "unit_value": 1e12,
        "unit_name": "/L",
        "reference_range": (4.3, 5.8)
    },
    "血红蛋白": {
        "abbr": "HGB",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (130, 175)
    },
    "红细胞比容": {
        "abbr": "HCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 50)
    },
    "平均红细胞容积": {
        "abbr": "MCV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (82, 100)
    },
    "平均红细胞血红蛋白量": {
        "abbr": "MCH",
        "unit_value": 1,
        "unit_name": "pg",
        "reference_range": (27, 34)
    },
    "平均红细胞血红蛋白浓度": {
        "abbr": "MCHC",
        "unit_value": 1,
        "unit_name": "g/L",
        "reference_range": (316, 354)
    },
    "血小板": {
        "abbr": "PLT",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (125, 350)
    },
    "红细胞分布宽度标准差": {
        "abbr": "RDW-SD",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (30, 54)
    },
    "红细胞分布宽度变异系数": {
        "abbr": "RDW-c",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 14.1)
    },
    "血小板体积分布宽度": {
        "abbr": "PDW",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 17)
    },
    "平均血小板体积": {
        "abbr": "MPV",
        "unit_value": 1,
        "unit_name": "fL",
        "reference_range": (9, 13)
    },
    "大血小板比率": {
        "abbr": "P-LCR",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (17.5, 30)
    },
    "血小板体积分数": {
        "abbr": "PCT",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.13, 0.35)
    },
    "中性粒细胞绝对值": {
        "abbr": "NEUT#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.8, 6.3)
    },
    "淋巴细胞绝对值": {
        "abbr": "LYMPH#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (1.1, 3.2)
    },
    "单核细胞绝对值": {
        "abbr": "MONO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.1, 0.6)
    },
    "嗜酸细胞绝对值": {
        "abbr": "EO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0.02, 0.52)
    },
    "嗜碱细胞绝对值": {
        "abbr": "BASO#",
        "unit_value": 1e9,
        "unit_name": "/L",
        "reference_range": (0, 0.06)
    },
    "中性粒细胞比率": {
        "abbr": "NEUT%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (40, 75)
    },
    "淋巴细胞比率": {
        "abbr": "LYMPH%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (20, 50)
    },
    "单核细胞比率": {
        "abbr": "MONO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (3, 10)
    },
    "嗜酸细胞比率": {
        "abbr": "EO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0.4, 8)
    },
    "嗜碱细胞比率": {
        "abbr": "BASO%",
        "unit_value": 1,
        "unit_name": "%",
        "reference_range": (0, 1)
    },
}


class BloodtestjudgementRewardCalculator(BaseRewardCalculator):
    """Bloodtestjudgement奖励计算器"""
    
    @staticmethod
    def extract_output(output: str):
        """
        Parse the LLM's raw text and return the last valid Python list of ints [-1,0,1].
        Ignores surrounding commentary and any earlier lists.
        """
        pattern = re.compile(r'\[\s*-?\d+\s*(?:,\s*-?\d+\s*)*\]')
        matches = pattern.findall(output)
        if not matches:
            return []

        last_literal = matches[-1]
        try:
            solution = ast.literal_eval(last_literal)        # safely turn the string into a list
            if isinstance(solution, (list, tuple)) and all(isinstance(x, (int, float)) for x in solution):
                return [int(t) for t in solution]
        except Exception as err:
            return []
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        ground_truths = identity['ground_truths']

        if len(solution) != len(ground_truths):
            return False
        
        return all(x == y for x, y in zip(solution, ground_truths))
    
    # 其他额外方法

