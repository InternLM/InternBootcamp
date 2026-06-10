from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.finance_bootcamp.finance_reward_calculator import FinanceRewardCalculator

class FinanceInteraction(BaseInteraction):
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
        extracted = FinanceRewardCalculator.extract_output(output_str=content)
        if extracted:
            return True, '', -1, {}
        else:
            return False, '请继续尝试，或者如果已找到答案，请务必使用规定格式输出。', -1, {}
    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        return super().calculate_score(instance_id, **kwargs)
    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        return super().finalize_interaction(instance_id, **kwargs)