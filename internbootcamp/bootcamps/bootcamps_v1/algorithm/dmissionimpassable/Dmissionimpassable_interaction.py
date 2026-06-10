from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dmissionimpassable.Dmissionimpassable_reward_calculator import DmissionimpassableRewardCalculator

# 导入依赖库
import re
import random




class DmissionimpassableInteraction(BaseInteraction):
    """Dmissionimpassable交互管理器"""
    
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
        score = DmissionimpassableRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dmissionimpassable问题！"""
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
    def _compute_max_score(cls, identity):
        s = identity['s']
        a = [x if x != -1 else -float('inf') for x in identity['a']]
        n = len(s)

        # Precompute palindrome table
        is_palin = [[False]*n for _ in range(n)]
        for i in range(n-1, -1, -1):
            for j in range(i, n):
                if i == j:
                    is_palin[i][j] = True
                elif i+1 == j:
                    is_palin[i][j] = (s[i] == s[j])
                else:
                    is_palin[i][j] = (s[i] == s[j] and is_palin[i+1][j-1])

        # Initialize DP tables
        dp = [[-float('inf')]*n for _ in range(n)]
        best = [[0]*n for _ in range(n)]

        for length in range(1, n+1):
            for i in range(n - length +1):
                j = i + length -1
                if length == 1:
                    dp[i][j] = a[0]
                else:
                    # Split into substrings
                    dp[i][j] = max([dp[i][k] + dp[k+1][j] for k in range(i, j)], default=-float('inf'))

                    # Check entire palindrome
                    if is_palin[i][j]:
                        dp[i][j] = max(dp[i][j], a[length-1])

                # Update best solution
                best[i][j] = max(0, dp[i][j])
                for k in range(i, j):
                    best[i][j] = max(best[i][j], best[i][k] + best[k+1][j])

        return best[0][n-1]
