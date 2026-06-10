from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.example_bootcamp.example_reward_calculator import ExampleRewardCalculator

class ExampleInteraction(BaseInteraction):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        Args:
            instance_id: str
            messages: list[dict[str, Any]]
        Returns:
            should_terminate_sequence: bool
            response_content: str
            current_turn_score: float
            additional_data: dict[str, Any]
        """
        content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                content = item.get("content")
                break
        score = ExampleRewardCalculator.verify_score(model_output=content, identity=self._instance_dict[instance_id]['identity'], format_score=0, short_penalty=False, short_threshold=256, think_threshold=0, ans_threshold=256, format_penalty=False)
        if score > 0.99:
            return True, '', score, {}
        else:
            return False, 'Your response is incorrect! You need to reflect on your answer and try again.', score, {}
    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        return super().calculate_score(instance_id, **kwargs)
    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        return super().finalize_interaction(instance_id, **kwargs)