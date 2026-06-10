from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.bdreamoonandwifi.Bdreamoonandwifi_reward_calculator import BdreamoonandwifiRewardCalculator

# 导入依赖库
import random
import math




class BdreamoonandwifiInteraction(BaseInteraction):
    """Bdreamoonandwifi交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = BdreamoonandwifiRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bdreamoonandwifi问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法
    @classmethod
    def _calculate_probability(cls, s1, s2):
        """ 精确的概率计算核心 """
        # 计算原始目标位置
        target_pos = sum(1 if c == '+' else -1 for c in s1)

        # 解析接收到的指令
        fixed_pos = 0
        unknown_count = 0
        for c in s2:
            if c == '+':
                fixed_pos += 1
            elif c == '-':
                fixed_pos -= 1
            else:
                unknown_count += 1

        # 计算需要补偿的位移
        required_offset = target_pos - fixed_pos

        # 检查是否可能满足
        if (required_offset + unknown_count) % 2 != 0:
            return 0.0
        if abs(required_offset) > unknown_count:
            return 0.0

        # 计算组合数
        k = (required_offset + unknown_count) // 2
        try:
            combinations = math.comb(unknown_count, k)
        except AttributeError:  # 兼容Python <3.10
            combinations = math.factorial(unknown_count) // (
                math.factorial(k) * math.factorial(unknown_count - k))

        return combinations / (2 ** unknown_count)
