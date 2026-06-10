import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehMultistepArithmeticRewardCalculator(BaseRewardCalculator):
    """依据标准答案验证多步算术任务的模型输出。"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[float]:
        if not output_str:
            return None

        matches = re.findall(r"\[answer\](.*?)\[/answer\]", output_str, flags=re.DOTALL | re.IGNORECASE)
        if not matches:
            return None

        candidate = matches[-1].strip()
        try:
            return float(candidate)
        except ValueError:
            return None

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[float], identity: dict, **kwargs) -> float:
        if extract_solution is None or identity is None:
            return 0.0

        expected = identity.get("answer")
        if expected is None:
            return 0.0

        try:
            if abs(float(extract_solution) - float(expected)) < 1e-6:
                return 1.0
        except (TypeError, ValueError):
            return 0.0
        return 0.0


