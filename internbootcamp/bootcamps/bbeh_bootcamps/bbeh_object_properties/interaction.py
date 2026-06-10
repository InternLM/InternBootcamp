from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_object_properties.reward_calculator import (
    BbehObjectPropertiesRewardCalculator,
)


def _latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehObjectPropertiesInteraction(BaseInteraction):
    """面向 BBEH Object Properties 任务的交互管理器。"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.95))
        self.success_feedback: str = config.get(
            "success_feedback",
            "属性追踪正确，请总结关键推理后结束本轮。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "答案未能通过验证，请再次核对最终集合的属性统计，并用[answer]X[/answer]返回整数或 unknown。",
        )
        self.verify_kwargs: Dict[str, Any] = config.get("verify_kwargs", {})

    async def start_interaction(
        self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs
    ) -> str:
        instance_id = await super().start_interaction(instance_id=instance_id, identity=identity, **kwargs)
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

        assistant_output = _latest_assistant_message(messages)
        if assistant_output is None:
            return (
                False,
                "暂未检测到你的最终回答，请根据题面推理并使用[answer][/answer]标记答案。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehObjectPropertiesRewardCalculator.verify_score(
            assistant_output,
            identity or {},
            **self.verify_kwargs,
        )

        attempts += 1
        state["attempts"] = attempts
        self._instance_dict[instance_id] = state

        should_terminate = score >= self.score_threshold
        feedback = self.success_feedback if should_terminate else self.retry_feedback

        return should_terminate, feedback, float(score), {
            "attempts": attempts,
            "score": float(score),
            "threshold": self.score_threshold,
        }
