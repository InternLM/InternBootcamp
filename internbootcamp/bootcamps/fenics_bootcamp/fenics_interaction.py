from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.fenics_bootcamp.fenics_reward_calculator import FenicsRewardCalculator


class ThermalInteraction(BaseInteraction):
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        严格复刻原始脚本的交互逻辑：
        1. 如果提取到格式答案 -> 终止交互 (should_terminate=True)。
        2. 如果未提取到 -> 继续交互，并返回固定的格式提示语。
        """
        # 1. 获取 Assistant 的最新回复内容
        content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                content = item.get("content")
                break
        
        # 获取当前任务上下文
        identity = self._instance_dict[instance_id]['identity']

        # 2. 尝试提取答案
        extracted_ans = FenicsRewardCalculator.extract_output(content)

        if extracted_ans is not None:
            # 只要提取到答案，立刻终止交互
            # 计算当前得分
            # score = FenicsRewardCalculator._verify_correction(extracted_ans, identity)
            
            # 返回: 终止=True, 反馈="", 得分, 额外信息
            return True, "", -1, {}
        
        else:
            # 未提取到答案，继续交互
            feedback = "请继续尝试调整热通量参数，或者如果已找到满足条件的参数，请务必使用 \\boxed{flux_left, flux_bottom} 格式输出最终答案。"
            
            # 返回: 终止=False, 反馈=固定提示语, 得分=0, 额外信息
            return False, feedback, -1, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        return super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        return super().finalize_interaction(instance_id, **kwargs)
