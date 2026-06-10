from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_hyperbaton.reward_calculator import (
    BbehHyperbatonRewardCalculator,
)


def _latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehHyperbatonInteraction(BaseInteraction):
    """Hyperbaton 形容词顺序任务的交互管理逻辑。"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.95))
        self.success_feedback: str = config.get(
            "success_feedback",
            "判断正确，请总结关键规律后结束对话。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "当前回答未通过验证，请重新比对示例与备选项，并以“最终答案: ”后接字母组合的格式作答。",
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
                "尚未检测到你的正式回答，请结合示例给出推理，并以“最终答案: ”后接字母组合结束回复。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehHyperbatonRewardCalculator.verify_score(
            assistant_output,
            identity or {},
            **self.verify_kwargs,
        )

        attempts += 1
        state["attempts"] = attempts
        self._instance_dict[instance_id] = state

        should_terminate = score >= self.score_threshold
        response = self.success_feedback if should_terminate else self.retry_feedback
        additional_data = {
            "attempts": attempts,
            "score": float(score),
            "threshold": self.score_threshold,
        }
        return should_terminate, response, float(score), additional_data


