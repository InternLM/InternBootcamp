from __future__ import annotations

import math
import re
from typing import Optional

from internbootcamp.src.base_reward_calculator import BaseRewardCalculator
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_buggy_tables.libs.bbeh_buggy_tables_solver import (
    BBEHBuggyTablesSolver,
)


class BbehBuggyTablesRewardCalculator(BaseRewardCalculator):
    """提取模型答案并基于求解器结果打分。"""

    _solver = BBEHBuggyTablesSolver()

    @staticmethod
    def extract_output(output_str: str) -> Optional[float]:
        if not output_str:
            return None
        candidates = re.findall(r"[-+]?\d*\.?\d+", output_str)
        if not candidates:
            return None
        try:
            return float(candidates[-1])
        except (TypeError, ValueError):
            return None

    @classmethod
    def _resolve_expected_answer(cls, identity: dict[str, object]) -> Optional[float]:
        expected = identity.get("expected_answer")
        if expected is not None:
            try:
                numeric_expected = float(expected)
            except (TypeError, ValueError):
                return None
            if math.isnan(numeric_expected):
                return None
            return numeric_expected

        input_payload = identity.get("input")
        if not isinstance(input_payload, dict):
            return None

        example = {
            "input": input_payload,
        }
        query_info = identity.get("query_info")
        if isinstance(query_info, dict):
            example["query_info"] = query_info

        result = cls._solver.solve(example)
        if result is None:
            return None
        try:
            numeric_result = float(result)
        except (TypeError, ValueError):
            return None
        if math.isnan(numeric_result):
            return None
        return numeric_result

    @classmethod
    def _verify_correction(
        cls,
        extract_solution: Optional[float],
        identity: dict[str, object],
        tolerance: float = 0.05,
        **kwargs,
    ) -> float:
        if extract_solution is None:
            return 0.0

        try:
            predicted = float(extract_solution)
        except (TypeError, ValueError):
            return 0.0

        expected = cls._resolve_expected_answer(identity or {})
        if expected is None:
            return 0.0

        diff = abs(predicted - expected)
        tolerance = float(kwargs.get("tolerance", tolerance))

        if diff <= tolerance:
            return 1.0
        return 0.0


