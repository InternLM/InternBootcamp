from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_object_counting.reward_calculator import (
    BbehObjectCountingRewardCalculator,
)


def _extract_latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehObjectCountingInteraction(BaseInteraction):
    """管理对象计数任务的对话与评分流程。"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.95))
        self.success_feedback: str = config.get(
            "success_feedback",
            "计数正确，请简要总结你的推理过程并结束本轮。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "答案未通过验证，请重新统计指定类别的物品，并确保以[answer]数字[/answer]格式返回结果。",
        )
        self.verify_kwargs: Dict[str, Any] = config.get("verify_kwargs", {})

    async def start_interaction(
        self,
        instance_id: Optional[str] = None,
        identity: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        instance_id = await super().start_interaction(instance_id=instance_id, identity=identity, **kwargs)
        if instance_id is not None:
            state = self._instance_dict.setdefault(instance_id, {})
            state.setdefault("attempts", 0)
        return instance_id

    async def generate_response(
        self,
        instance_id: str,
        messages: list[dict[str, Any]],
        **kwargs,
    ) -> tuple[bool, str, float, dict[str, Any]]:
        state = self._instance_dict.get(instance_id, {})
        identity = state.get("identity")
        attempts = int(state.get("attempts", 0))

        assistant_output = _extract_latest_assistant_message(messages)
        if assistant_output is None:
            return (
                False,
                "尚未检测到你的正式回答，请根据题目给出明确的数值并使用[answer][/answer]包裹。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehObjectCountingRewardCalculator.verify_score(
            assistant_output,
            identity or {},
            **self.verify_kwargs,
        )

        attempts += 1
        state["attempts"] = attempts
        self._instance_dict[instance_id] = state

        should_terminate = float(score) >= self.score_threshold
        feedback = self.success_feedback if should_terminate else self.retry_feedback
        additional_data = {
            "attempts": attempts,
            "score": float(score),
            "threshold": self.score_threshold,
        }
        return should_terminate, feedback, float(score), additional_data

