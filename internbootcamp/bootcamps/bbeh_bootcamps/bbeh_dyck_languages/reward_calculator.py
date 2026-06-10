import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehDyckLanguagesRewardCalculator(BaseRewardCalculator):
    """从模型输出中提取答案并根据首个错误步骤进行判分。"""

    @staticmethod
    def extract_output(output_str: str) -> Optional[str]:
        if not output_str:
            return None

        matches = re.findall(r'\[answer\]\s*(\d+|No)\s*\[/answer\]', output_str, flags=re.IGNORECASE)
        if not matches:
            matches = re.findall(r'\b(\d+|No)\b', output_str, flags=re.IGNORECASE)
        if not matches:
            return None

        final = matches[-1].strip()
        if final.lower() == "no":
            return "No"

        digits = re.findall(r'\d+', final)
        if not digits:
            return None
        return str(int(digits[-1]))

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[str], identity: dict, **kwargs) -> float:
        if extract_solution is None or not isinstance(identity, dict):
            return 0.0

        expected_error = identity.get("error_step")
        if expected_error is None:
            return 1.0 if extract_solution.lower() == "no" else 0.0

        try:
            predicted_step = int(extract_solution)
        except (TypeError, ValueError):
            return 0.0

        try:
            expected_step = int(expected_error)
        except (TypeError, ValueError):
            return 0.0

        return 1.0 if predicted_step == expected_step else 0.0


