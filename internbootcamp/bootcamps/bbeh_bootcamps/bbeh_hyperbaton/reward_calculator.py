import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehHyperbatonRewardCalculator(BaseRewardCalculator):
    """根据模型输出提取选项并与标准答案对比。"""

    FINAL_ANSWER_PATTERN = re.compile(
        r"(?:最终答案|Final Answer)\s*[:：]\s*([A-K]+)",
        re.IGNORECASE,
    )
    LETTER_SEQUENCE_PATTERN = re.compile(r"\b([A-K]{1,10})\b")

    @staticmethod
    def extract_output(output_str: Optional[str]) -> Optional[str]:
        if not output_str:
            return None

        matches = BbehHyperbatonRewardCalculator.FINAL_ANSWER_PATTERN.findall(output_str)
        if not matches:
            matches = BbehHyperbatonRewardCalculator.LETTER_SEQUENCE_PATTERN.findall(output_str)
        if not matches:
            return None

        candidate = matches[-1].upper()
        letters = "".join(ch for ch in candidate if ch in "ABCDEFGHIJK")
        if not letters:
            return None
        return letters

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[str], identity: dict, **kwargs) -> float:
        if extract_solution is None or not isinstance(identity, dict):
            return 0.0

        expected = identity.get("target")
        if not expected:
            return 0.0
        if extract_solution == expected:
            return 1.0
        return 0.0


