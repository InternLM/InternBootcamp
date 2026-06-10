from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctanyaandcoloredcandies.Ctanyaandcoloredcandies_reward_calculator import CtanyaandcoloredcandiesRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_candy_boxes(n, s, k, r_list, color_str):
    s -= 1  # 转换为0-based索引
    r = r_list
    color = color_str
    INF = float('inf')
    
    # 预处理最大可能的糖果数
    max_possible = sum(r)
    if max_possible < k:
        return -1
    
    # 动态规划数组，dp[cur][c]表示从cur出发，获得至少c颗糖果的最短时间
    dp = [[INF] * (k + 1) for _ in range(n)]
    
    # 预处理每个盒子自身的情况
    for i in range(n):
        current_max = min(r[i], k)
        for c in range(current_max + 1):
            dp[i][c] = 0  # 只需要吃当前盒子即可
        
    # 记忆化搜索函数
    def dfs(cur):
        # 已经处理过的情况直接返回
        if dp[cur][k] != INF:
            return
        
        # 尝试所有可能的后继盒子
        for to in range(n):
            if color[to] != color[cur] and r[to] > r[cur]:
                dfs(to)
                distance = abs(cur - to)
                
                # 状态转移：当前吃掉的糖果数 + 后续吃掉的糖果数
                for c in range(k, -1, -1):
                    if dp[cur][c] == INF:
                        continue
                    
                    # 计算转移后的糖果数
                    new_c = min(c + r[to], k)
                    cost = dp[cur][c] + distance
                    if cost < dp[to][new_c]:
                        dp[to][new_c] = cost
                        # 回溯更新所有可能的更优解
                        for nc in range(new_c, k+1):
                            if dp[to][nc] > cost:
                                dp[to][nc] = cost
    
    # 从每个可能的起点开始计算
    for i in range(n):
        dfs(i)
    
    # 计算最小时间
    min_time = INF
    for i in range(n):
        start_cost = abs(i - s)
        if start_cost + dp[i][k] < min_time:
            min_time = start_cost + dp[i][k]
    
    return min_time if min_time != INF else -1


class CtanyaandcoloredcandiesInteraction(BaseInteraction):
    """Ctanyaandcoloredcandies交互管理器"""
    
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
        score = CtanyaandcoloredcandiesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ctanyaandcoloredcandies问题！"""
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

