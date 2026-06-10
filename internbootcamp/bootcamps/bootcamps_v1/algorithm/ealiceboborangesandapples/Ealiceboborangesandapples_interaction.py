from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ealiceboborangesandapples.Ealiceboborangesandapples_reward_calculator import EaliceboborangesandapplesRewardCalculator

# 导入依赖库
import math
import re
import random




class EaliceboborangesandapplesInteraction(BaseInteraction):
    """Ealiceboborangesandapples交互管理器"""
    
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
        score = EaliceboborangesandapplesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ealiceboborangesandapples问题！"""
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
    def decompress(cls, compressed):
        if not re.fullmatch(r'([1-9]\d*[AB])+', compressed):
            return None

        parts = re.findall(r'([1-9]\d*)([AB])', compressed)
        return ''.join(c * int(n) for n, c in parts)

    @classmethod
    def validate_sequence(cls, sequence, x, y):
        bag_orange = x - 1
        bag_apple = y - 1
        a_orange, a_apple = 1, 0
        b_orange, b_apple = 0, 1

        for c in sequence:
            if c == 'A':
                transfer_orange = a_orange
                transfer_apple = a_apple
                new_a_orange = a_orange
                new_a_apple = a_apple
                if (transfer_orange > bag_orange) or (transfer_apple > bag_apple):
                    return False

                b_orange += transfer_orange
                b_apple += transfer_apple
                bag_orange -= transfer_orange
                bag_apple -= transfer_apple

                a_orange = new_a_orange
                a_apple = new_a_apple

            elif c == 'B':
                transfer_orange = b_orange
                transfer_apple = b_apple
                new_b_orange = b_orange
                new_b_apple = b_apple
                if (transfer_orange > bag_orange) or (transfer_apple > bag_apple):
                    return False

                a_orange += transfer_orange
                a_apple += transfer_apple
                bag_orange -= transfer_orange
                bag_apple -= transfer_apple

                b_orange = new_b_orange
                b_apple = new_b_apple

            else:
                return False

        return bag_orange == 0 and bag_apple == 0
