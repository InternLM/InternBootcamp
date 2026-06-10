from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator


def last_boxed_only_string(string: str) -> Optional[str]:
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        return None
    return string[idx : right_brace_idx + 1]


def remove_boxed(text: str) -> str:
    if text.startswith("\\boxed "):
        return text[len("\\boxed ") :]
    if text.startswith("\\boxed{") and text.endswith("}"):
        return text[len("\\boxed{") : -1]
    if text.startswith("\\fbox{") and text.endswith("}"):
        return text[len("\\fbox{") : -1]
    return text


class BbehGeometricShapesRewardCalculator(BaseRewardCalculator):
    """根据模型输出提取答案并与标准答案比较。"""

    @staticmethod
    def extract_output(output_str: Optional[str]) -> Optional[str]:
        if not output_str:
            return None
        extracted = last_boxed_only_string(output_str)
        if extracted is None:
            return None
        cleaned = remove_boxed(extracted).strip()
        if not cleaned:
            return None
        return cleaned

    @classmethod
    def _verify_correction(cls, extract_solution: Optional[str], identity: dict, **kwargs) -> float:
        if extract_solution is None or not isinstance(identity, dict):
            return 0.0
        expected = identity.get("ans")
        if expected is None:
            return 0.0
        if str(extract_solution).strip() == str(expected).strip():
            return 1.0
        return 0.0


