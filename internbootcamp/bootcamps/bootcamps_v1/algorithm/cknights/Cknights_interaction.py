from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cknights.Cknights_reward_calculator import CknightsRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def simulate_knights_placement(initial_knights):
    current_knights = set()
    coords = [tuple(knight) for knight in initial_knights]
    if len(coords) != len(set(coords)):
        return 0
    for x, y in coords:
        if not (-1e9 <= x <= 1e9 and -1e9 <= y <= 1e9):
            return 0
    current_knights = set(coords)
    knight_moves = [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]
    attack_counts = defaultdict(int)
    for x, y in current_knights:
        for dx, dy in knight_moves:
            neighbor = (x + dx, y + dy)
            attack_counts[neighbor] += 1
    queue = deque()
    in_queue = set()
    for cell in attack_counts:
        if attack_counts[cell] >=4 and cell not in current_knights:
            queue.append(cell)
            in_queue.add(cell)
    while queue:
        cell = queue.popleft()
        in_queue.discard(cell)
        if cell in current_knights:
            continue
        if attack_counts[cell] <4:
            continue
        current_knights.add(cell)
        for dx, dy in knight_moves:
            neighbor = (cell[0] + dx, cell[1] + dy)
            attack_counts[neighbor] += 1
            if attack_counts[neighbor] >=4 and neighbor not in current_knights and neighbor not in in_queue:
                queue.append(neighbor)
                in_queue.add(neighbor)
    return len(current_knights)


class CknightsInteraction(BaseInteraction):
    """Cknights交互管理器"""
    
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
        score = CknightsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cknights问题！"""
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

