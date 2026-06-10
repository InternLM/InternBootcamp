from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_boolean_expressions.reward_calculator import (
    BbehBooleanExpressionsRewardCalculator,
)


def _extract_latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehBooleanExpressionsInteraction(BaseInteraction):
    """针对布尔表达式任务的交互管理逻辑。"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.99))
        self.success_feedback: str = config.get(
            "success_feedback",
            "推理正确，请简要总结你的判断依据并结束本轮。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "当前回答未通过验证，请重新检查五个表达式的真值，注意使用[answer]X[/answer]格式返回答案。",
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

        assistant_output = _extract_latest_assistant_message(messages)
        if assistant_output is None:
            return (
                False,
                "尚未检测到你的正式回答，请结合题目给出推理过程，并使用[answer][/answer]标记最终结论。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehBooleanExpressionsRewardCalculator.verify_score(
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

