import re
from typing import Optional, Union

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehObjectPropertiesRewardCalculator(BaseRewardCalculator):
    """提取模型输出并验证 BBEH Object Properties 答案。"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[Union[int, str]]:
        if not output_str:
            return None

        matches = re.findall(r"<answer>(.*?)</answer>", output_str, flags=re.IGNORECASE | re.DOTALL)
        if not matches:
            return None

        raw = matches[-1].strip()
        if not raw:
            return None

        if raw.lower() == "unknown":
            return "unknown"

        numbers = re.findall(r"-?\d+", raw)
        if not numbers:
            return None

        try:
            return int(numbers[-1])
        except ValueError:
            return None

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[Union[int, str]], identity: dict, **kwargs) -> float:
        if identity is None or not isinstance(identity, dict):
            return 0.0

        answer = identity.get("answer")
        if answer is None:
            return 0.0

        if isinstance(extract_solution, str) and extract_solution.lower() == "unknown":
            return 1.0 if str(answer).lower() == "unknown" else 0.0

        try:
            expected = int(answer)
        except (TypeError, ValueError):
            return 0.0

        try:
            extracted_value = int(extract_solution) if not isinstance(extract_solution, int) else extract_solution
        except (TypeError, ValueError):
            return 0.0

        return 1.0 if extracted_value == expected else 0.0
