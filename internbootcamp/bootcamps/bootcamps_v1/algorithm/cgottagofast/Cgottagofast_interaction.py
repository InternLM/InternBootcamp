from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cgottagofast.Cgottagofast_reward_calculator import CgottagofastRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_expected_time(n, r, levels):
    a = levels
    left = 0.0
    right = 1e18
    answer = 0.0
    dp = [[0.0] * 5001 for _ in range(n + 2)]

    for _ in range(100):
        middle = (left + right) / 2
        for i in range(n + 1):
            for j in range(5001):
                dp[i][j] = 0.0

        for i in range(n - 1, -1, -1):
            for j in range(r + 1, 5001):
                dp[i + 1][j] = middle
            Fi, Si, Pi = a[i]
            p = Pi / 100.0
            q = (100 - Pi) / 100.0
            for j in range(r, -1, -1):
                fast = j + Fi
                slow = j + Si
                val_fast = Fi + (dp[i + 1][fast] if fast <= r else middle)
                val_slow = Si + (dp[i + 1][slow] if slow <= r else middle)
                expected = p * val_fast + q * val_slow
                dp[i][j] = min(middle, expected)
        if dp[0][0] < middle - 1e-12:
            answer = middle
            right = middle
        else:
            left = middle
    return answer


class CgottagofastInteraction(BaseInteraction):
    """Cgottagofast交互管理器"""
    
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
        score = CgottagofastRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cgottagofast问题！"""
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

