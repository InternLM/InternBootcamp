from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dnewyearandancientprophecy.Dnewyearandancientprophecy_reward_calculator import DnewyearandancientprophecyRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, digits_str):
    if n == 0:
        return 0
    d = [int(c) for c in digits_str]
    if n == 1:
        return 1
    
    # Initialize comparison matrix
    comp = [[0]*(n+1) for _ in range(n)]
    
    for l in range(1, n):
        equal_count = 0
        for i in range(n - l):
            j = i + l
            if d[i] == d[j]:
                equal_count += 1
                if equal_count >= l:
                    equal_count = l - 1
            else:
                if d[i] < d[j]:
                    # Mark all positions in the equal prefix
                    start = i - equal_count
                    end = i + 1
                    for k in range(start, end):
                        if k >= 0 and j - equal_count + (k - start) < n:
                            comp[k][j - equal_count + (k - start) + 1] = 1
                equal_count = 0
    
    # Dynamic programming table
    dp = [[0]*(n+1) for _ in range(n+1)]
    for j in range(1, n+1):
        dp[j][j] = 1
    
    # Fill DP table
    for i in range(1, n):
        if d[i] == 0:
            continue
        prefix_sum = 0
        for l in range(1, n - i + 1):
            prefix_sum = (prefix_sum + dp[i][l-1]) % MOD
            if l <= i:
                compare_pos = i - l
                if compare_pos >= 0 and comp[compare_pos][i]:
                    dp[i+l][l] = (prefix_sum + dp[i][l]) % MOD
                else:
                    dp[i+l][l] = prefix_sum
            else:
                dp[i+l][l] = prefix_sum
    
    # Calculate final answer
    total = 0
    for l in range(1, n+1):
        total = (total + dp[n][l]) % MOD
    return total


class DnewyearandancientprophecyInteraction(BaseInteraction):
    """Dnewyearandancientprophecy交互管理器"""
    
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
        score = DnewyearandancientprophecyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dnewyearandancientprophecy问题！"""
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

