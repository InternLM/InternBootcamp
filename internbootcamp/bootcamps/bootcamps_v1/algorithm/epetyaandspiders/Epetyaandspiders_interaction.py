from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.epetyaandspiders.Epetyaandspiders_reward_calculator import EpetyaandspidersRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def get_bit(a, n):
    return (a >> n) & 1

def reset_bit(a, n):
    return a & ~(1 << n)

def calculate_max_empty(n, m):
    # Ensure n is the larger dimension for optimization
    if m > n:
        n, m = m, n
    if m == 0:
        return 0  # Should not happen for valid input
    max_size = 1 << m
    dp = [[[-1000] * max_size for _ in range(max_size)] for __ in range(n + 1)]
    initial_mask = (1 << m) - 1
    dp[0][0][initial_mask] = 0
    
    for i in range(1, n + 1):
        for prev_row in range(max_size):
            for prev_mask in range(max_size):
                if dp[i-1][prev_row][prev_mask] == -1000:
                    continue
                for current_row in range(max_size):
                    # Calculate spiders present in current configuration
                    combined = prev_row | current_row
                    cnt = sum(1 for bit in range(m) if not get_bit(combined, bit))
                    
                    # Calculate new_mask based on spider movements
                    new_mask = initial_mask
                    for bit in range(m):
                        if get_bit(combined, bit):
                            if m == 1:
                                new_mask = reset_bit(new_mask, 0)
                            else:
                                for offset in (-1, 0, 1):
                                    pos = bit + offset
                                    if 0 <= pos < m:
                                        new_mask = reset_bit(new_mask, pos)
                    
                    next_mask = new_mask & prev_mask
                    dp[i][next_mask][current_row] = max(
                        dp[i][next_mask][current_row], 
                        dp[i-1][prev_row][prev_mask] + cnt
                    )
    
    # Find maximum value in final state
    return max(dp[n][0][state] for state in range(max_size))


class EpetyaandspidersInteraction(BaseInteraction):
    """Epetyaandspiders交互管理器"""
    
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
        score = EpetyaandspidersRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Epetyaandspiders问题！"""
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

