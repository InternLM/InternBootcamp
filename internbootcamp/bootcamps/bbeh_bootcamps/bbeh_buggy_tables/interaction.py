from __future__ import annotations

from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_buggy_tables.reward_calculator import (
    BbehBuggyTablesRewardCalculator,
)


def _extract_latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehBuggyTablesInteraction(BaseInteraction):
    """针对 Buggy Tables 任务的交互流程。"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.95))
        self.success_feedback: str = config.get(
            "success_feedback",
            "答案已通过验证，可以简要总结修复思路并结束本轮。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "结果未通过验证，请重新检查数据修复和查询计算，确保以“最终答案: 数值”格式给出结论。",
        )
        self.verify_kwargs: Dict[str, Any] = config.get("verify_kwargs", {})

    async def start_interaction(
        self,
        instance_id: Optional[str] = None,
        identity: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        instance_id = await super().start_interaction(
            instance_id=instance_id, identity=identity, **kwargs
        )
        if instance_id is not None:
            state = self._instance_dict.setdefault(instance_id, {})
            state.setdefault("attempts", 0)
        return instance_id

    async def generate_response(
        self, instance_id: str, messages: list[dict[str, Any]], **kwargs
    ) -> tuple[bool, str, float, dict[str, Any]]:
        state = self._instance_dict.get(instance_id, {})
        identity = state.get("identity")
        attempts = state.get("attempts", 0)

        assistant_output = _extract_latest_assistant_message(messages)
        if assistant_output is None:
            return (
                False,
                "尚未检测到有效回答，请给出修复表格的关键步骤，并以“最终答案: 数值”输出结论。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehBuggyTablesRewardCalculator.verify_score(
            assistant_output,
            identity or {},
            **self.verify_kwargs,
        )

        attempts += 1
        state["attempts"] = attempts
        self._instance_dict[instance_id] = state

        should_terminate = score >= self.score_threshold
        if score >= self.score_threshold:
            response = self.success_feedback
        else:
            response = self.retry_feedback

        additional_data = {
            "attempts": attempts,
            "score": float(score),
            "threshold": self.score_threshold,
        }
        return should_terminate, response, float(score), additional_data


