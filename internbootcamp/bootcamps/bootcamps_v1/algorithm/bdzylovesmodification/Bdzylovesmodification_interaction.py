from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bdzylovesmodification.Bdzylovesmodification_reward_calculator import BdzylovesmodificationRewardCalculator

# 导入依赖库
import heapq
from heapq import heappush
from heapq import heappop
import random

# === 源文件中的全局函数 ===

def calculate_max_pleasure(n, m, k, p, matrix):
    # 计算初始行和列的总和
    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(n)) for j in range(m)]

    # 初始化最大堆（使用负数实现最小堆模拟最大堆）
    row_heap = [-s for s in row_sums]
    heapq.heapify(row_heap)
    col_heap = [-s for s in col_sums]
    heapq.heapify(col_heap)

    # 预计算所有可能的行操作收益
    pr = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not row_heap:
            break
        current = -heappop(row_heap)
        current_sum += current
        pr[h] = current_sum
        heappush(row_heap, -(current - m*p))  # 更新行总和

    # 预计算所有可能的列操作收益
    pc = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not col_heap:
            break
        current = -heappop(col_heap)
        current_sum += current
        pc[h] = current_sum
        heappush(col_heap, -(current - n*p))  # 更新列总和

    # 穷举所有可能的行、列操作组合
    max_total = -float('inf')
    for i in pr:
        j = k - i
        if j >= 0 and j in pc:
            total = pr[i] + pc[j] - i*j*p
            max_total = max(max_total, total)
    
    return max_total if max_total != -float('inf') else 0


class BdzylovesmodificationInteraction(BaseInteraction):
    """Bdzylovesmodification交互管理器"""
    
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
        score = BdzylovesmodificationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bdzylovesmodification问题！"""
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

