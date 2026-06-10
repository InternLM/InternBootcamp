from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.crememberingstrings.Crememberingstrings_reward_calculator import CrememberingstringsRewardCalculator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def solve(n, m, strings, costs):
    faa = [[0] * m for _ in range(n)]
    famask = [[0] * m for _ in range(n)]
    
    for i in range(n):
        for j in range(m):
            current_char = strings[i][j]
            total_cost = 0
            max_cost = 0
            mask = 0
            for k in range(n):
                if strings[k][j] == current_char:
                    total_cost += costs[k][j]
                    if costs[k][j] > max_cost:
                        max_cost = costs[k][j]
                    mask |= (1 << k)
            faa[i][j] = total_cost - max_cost
            famask[i][j] = mask
    
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        for j in range(n):
            if (mask >> j) & 1:
                continue
            for k in range(m):
                new_mask1 = mask | (1 << j)
                cost1 = dp[mask] + costs[j][k]
                if cost1 < dp[new_mask1]:
                    dp[new_mask1] = cost1
                
                new_mask2 = mask | famask[j][k]
                cost2 = dp[mask] + faa[j][k]
                if cost2 < dp[new_mask2]:
                    dp[new_mask2] = cost2
    
    return dp[(1 << n) - 1]


class CrememberingstringsInteraction(BaseInteraction):
    """Crememberingstrings交互管理器"""
    
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
        score = CrememberingstringsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Crememberingstrings问题！"""
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

