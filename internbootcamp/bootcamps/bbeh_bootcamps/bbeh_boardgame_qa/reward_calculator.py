import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehBoardgameQARewardCalculator(BaseRewardCalculator):
    """根据模型输出判断是否正确回答了 boardgame QA 问题"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[str]:
        if not output_str:
            return None

        candidates = re.findall(r'\[answer\](.*?)\[/answer\]', output_str, re.DOTALL | re.IGNORECASE)
        if not candidates:
            candidates = re.findall(r'\b(proved|disproved|unknown)\b', output_str, re.IGNORECASE)
        if not candidates:
            return None

        final = candidates[-1].strip().lower()
        if final in {'proved', 'disproved', 'unknown'}:
            return final
        return None

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[str], identity: dict, **kwargs) -> float:
        if not identity or extract_solution is None:
            return 0.0

        answer = identity.get("answer")
        if answer is None:
            return 0.0

        if extract_solution.lower() == str(answer).lower():
            return 1.0
        return 0.0

