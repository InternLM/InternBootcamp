from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dtopsecrettask.Dtopsecrettask_reward_calculator import DtopsecrettaskRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_loquacity(n, k, s, q):
    adjusted_s = min(s, (n*n)//2 + 10)  # 严格模拟参考代码的调整逻辑
    INF = float('inf')
    
    # 初始化DP数组，使用滚动数组优化
    dp = [[[INF] * (adjusted_s + 1) for _ in range(k+1)] for __ in range(2)]
    dp[0][0][0] = 0  # 初始状态

    for i in range(1, n+1):
        current = i % 2
        prev = 1 - current
        
        # 重置当前层
        for j in range(k+1):
            for t in range(adjusted_s + 1):
                dp[current][j][t] = INF
        
        # 状态转移
        for pref in range(0, min(i-1, k)+1):
            for done in range(adjusted_s + 1):
                if dp[prev][pref][done] == INF:
                    continue
                
                # 情况1：不选当前士兵
                if dp[current][pref][done] > dp[prev][pref][done]:
                    dp[current][pref][done] = dp[prev][pref][done]
                
                # 情况2：选当前士兵
                new_pref = pref + 1
                if new_pref > k:
                    continue
                
                swaps_needed = i - new_pref  # 与参考代码完全一致的计算方式
                new_done = done + swaps_needed
                
                if new_done <= adjusted_s:
                    new_value = dp[prev][pref][done] + q[i-1]
                    if new_value < dp[current][new_pref][new_done]:
                        dp[current][new_pref][new_done] = new_value
        
    # 寻找最终答案
    final_layer = n % 2
    return min(dp[final_layer][k][:adjusted_s+1])


class DtopsecrettaskInteraction(BaseInteraction):
    """Dtopsecrettask交互管理器"""
    
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
        score = DtopsecrettaskRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dtopsecrettask问题！"""
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

