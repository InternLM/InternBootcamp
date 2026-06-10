from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ehills.Ehills_reward_calculator import EhillsRewardCalculator

# 导入依赖库
import math
import random
from typing import List

# === 源文件中的全局函数 ===

def compute_min_time(n: int, a_list: List[int]) -> List[int]:
    INF = float('inf')
    high = [-INF] + a_list.copy() + [-INF]
    m = math.ceil(n / 2)
    
    # 初始化DP表，使用二维列表表示当前j和状态0/1/2的最小时间
    dp = [[INF] * 3 for _ in range(m + 1)]
    dp[0][0] = 0  # 初始状态：0个峰，最后状态是0（未选）
    
    for i in range(1, n + 1):
        new_dp = [[INF] * 3 for _ in range(m + 1)]
        for j in range(m + 1):
            for state in range(3):
                if dp[j][state] == INF:
                    continue
                
                if state == 0:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，转移到状态1
                    if j < m:
                        cost = 0
                        if high[i] <= high[i - 1]:
                            cost += high[i - 1] - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
                
                elif state == 1:
                    # 当前必须不选i（连续不能选），转移到状态2
                    new_dp[j][2] = min(new_dp[j][2], dp[j][state])
                
                elif state == 2:
                    # 当前不选i，转移到状态0
                    new_dp[j][0] = min(new_dp[j][0], dp[j][state])
                    # 选择i作为峰，需考虑前前一个峰的影响
                    if j < m:
                        cost = 0
                        prev_peak_height = high[i - 1]
                        # 考虑i-2的影响
                        if i >= 2 and high[i - 2] <= prev_peak_height:
                            prev_peak_height = high[i - 2] - 1
                        # 计算当前i需要调整的高度
                        if high[i] <= prev_peak_height:
                            cost += prev_peak_height - high[i] + 1
                        if high[i] <= high[i + 1]:
                            cost += high[i + 1] - high[i] + 1
                        new_dp[j + 1][1] = min(new_dp[j + 1][1], dp[j][state] + cost)
        dp = new_dp
    
    # 收集结果
    result = []
    for k in range(1, m + 1):
        min_val = min(dp[k][0], dp[k][1], dp[k][2])
        result.append(min_val if min_val != INF else 0)
    return result


class EhillsInteraction(BaseInteraction):
    """Ehills交互管理器"""
    
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
        score = EhillsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ehills问题！"""
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

