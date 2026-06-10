import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehObjectCountingRewardCalculator(BaseRewardCalculator):
    """负责提取模型答案并验证是否与目标数量相符。"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[int]:
        if not output_str:
            return None

        candidates = re.findall(r"\[answer\](.*?)\[/answer\]", output_str, flags=re.IGNORECASE | re.DOTALL)
        if not candidates:
            return None

        raw = candidates[-1].strip().replace(",", "")
        if "=" in raw:
            raw = raw.split("=")[-1].strip()

        number_matches = re.findall(r"-?\d+", raw)
        if not number_matches:
            return None
        try:
            return int(number_matches[-1])
        except ValueError:
            return None

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[int], identity: dict, **kwargs) -> float:
        if extract_solution is None or not isinstance(identity, dict):
            return 0.0

        answer = identity.get("answer")
        if answer is None:
            return 0.0

        try:
            return 1.0 if int(extract_solution) == int(answer) else 0.0
        except (TypeError, ValueError):
            return 0.0

