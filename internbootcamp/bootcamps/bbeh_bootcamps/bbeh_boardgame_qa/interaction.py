from typing import Any, Dict, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_boardgame_qa.reward_calculator import (
    BbehBoardgameQARewardCalculator,
)


def _extract_latest_assistant_message(messages: list[dict[str, Any]]) -> Optional[str]:
    for message in reversed(messages):
        if message.get("role") == "assistant":
            return message.get("content")
    return None


class BbehBoardgameQAInteraction(BaseInteraction):
    """基于得分的交互管理：分数低于阈值时提示模型重试"""

    def __init__(self, config: dict[str, Any], *args, **kwargs):
        super().__init__(config, *args, **kwargs)
        self.score_threshold: float = float(config.get("score_threshold", 0.9))
        self.success_feedback: str = config.get(
            "success_feedback",
            "很好，你的回答已通过验证，请总结本轮推理并结束。",
        )
        self.retry_feedback: str = config.get(
            "retry_feedback",
            "当前回答未能通过验证，请重新审视规则与事实，并再次给出最终结论，注意使用[answer][/answer]格式。",
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
                "尚未看到你的正式回答，请结合题目给出完整结论，并使用[answer][/answer]标记最终答案。",
                0.0,
                {"attempts": attempts, "reason": "no_assistant_message"},
            )

        score = BbehBoardgameQARewardCalculator.verify_score(
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
            "score": score,
            "threshold": self.score_threshold,
        }
        return should_terminate, response, float(score), additional_data

