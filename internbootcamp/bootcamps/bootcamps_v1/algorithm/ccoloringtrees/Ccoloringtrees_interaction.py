from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccoloringtrees.Ccoloringtrees_reward_calculator import CcoloringtreesRewardCalculator

# 导入依赖库
import json
import random
import re

# === 源文件中的全局函数 ===

def solve(n, m, k, c_list, p_matrix):
    INF = 10**18
    c = c_list
    p = p_matrix

    # DP优化算法实现
    dp = [[INF]*(m+1) for _ in range(k+1)]
    dp[0][0] = 0  # 初始状态
    
    for tree_idx in range(n):
        current_color = c[tree_idx]
        new_dp = [[INF]*(m+1) for _ in range(k+1)]
        
        for groups in range(k+1):
            for prev_color in range(m+1):
                if dp[groups][prev_color] == INF:
                    continue
                
                for new_color in range(1, m+1):
                    if current_color != 0 and current_color != new_color:
                        continue  # 已染色树不能改变颜色
                    
                    # 计算新分组数
                    new_groups = groups + (1 if new_color != prev_color else 0)
                    if new_groups > k:
                        continue
                    
                    # 计算成本
                    cost = p[tree_idx][new_color-1] if current_color == 0 else 0
                    
                    new_dp[new_groups][new_color] = min(
                        new_dp[new_groups][new_color],
                        dp[groups][prev_color] + cost
                    )
        
        dp = new_dp

    min_cost = min(dp[k][color] for color in range(1, m+1))
    return min_cost if min_cost < INF else -1


class CcoloringtreesInteraction(BaseInteraction):
    """Ccoloringtrees交互管理器"""
    
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
        score = CcoloringtreesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccoloringtrees问题！"""
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

