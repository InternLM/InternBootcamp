import re
from typing import Dict, Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


class BbehShuffObjectRewardCalculator(BaseRewardCalculator):
    """提取模型输出并验证 BBEH Shuffle Object 答案。"""

    @staticmethod
    def extract_output(output: str) -> Optional[str]:
        if not output:
            return None

        matches = re.findall(r"<answer>(.*?)</answer>", output, flags=re.IGNORECASE | re.DOTALL)
        if not matches:
            return None

        return matches[-1].strip()

    @classmethod
    def _verify_correction(cls, solution: Optional[str], identity: Dict, **kwargs) -> float:
        if solution is None or not identity:
            return 0.0

        correct_answer = identity.get("correct_answer")
        if correct_answer is None:
            return 0.0

        return 1.0 if solution.strip().lower() == str(correct_answer).strip().lower() else 0.0

