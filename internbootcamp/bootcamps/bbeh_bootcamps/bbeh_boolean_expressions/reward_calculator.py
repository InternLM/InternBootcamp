import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehBooleanExpressionsRewardCalculator(BaseRewardCalculator):
    """提取模型答案并根据标准答案计算得分。"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[str]:
        if not output_str:
            return None

        candidates = re.findall(r'\[answer\](.*?)\[/answer\]', output_str, flags=re.DOTALL | re.IGNORECASE)
        if not candidates:
            candidates = re.findall(r'\b([A-E])\b', output_str, flags=re.IGNORECASE)
        if not candidates:
            return None

        final = candidates[-1].strip().upper()
        if not final:
            return None
        letter = final[0]
        if letter in {'A', 'B', 'C', 'D', 'E'}:
            return letter
        return None

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[str], identity: dict, **kwargs) -> float:
        if extract_solution is None or not isinstance(identity, dict):
            return 0.0

        answer_index = identity.get("answer")
        if answer_index is None:
            return 0.0
        try:
            expected_letter = chr(ord('A') + int(answer_index))
        except (TypeError, ValueError):
            return 0.0

        if extract_solution == expected_letter:
            return 1.0
        return 0.0

