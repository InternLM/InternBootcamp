from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctrack.Ctrack_reward_calculator import CtrackRewardCalculator

# 导入依赖库
import random
import re
from heapq import heappop
from heapq import heappush

# === 源文件中的全局函数 ===

def manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def solve(n, m, k, mat):
    start = None
    end = None
    for i in range(n):
        for j in range(m):
            if mat[i][j] == 'S':
                start = (i, j)
            elif mat[i][j] == 'T':
                end = (i, j)
    if not start or not end:
        return "-1"
    br, bc = start
    er, ec = end

    heap = []
    initial_priority = manhattan(br, bc, er, ec)
    heappush(heap, (initial_priority, '', 0, br, bc, 0, ''))
    ha = {i: {j: set() for j in range(m)} for i in range(n)}

    while heap:
        priority, path, steps, r, c, cu, used_str = heappop(heap)
        if (r, c) == (er, ec):
            return path
        if used_str in ha[r][c]:
            continue
        ha[r][c].add(used_str)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                ch = mat[nr][nc]
                if ch == 'S':
                    continue
                new_steps = steps + 1
                new_priority = new_steps + manhattan(nr, nc, er, ec)
                if ch == 'T':
                    heappush(heap, (new_priority, path, new_steps, nr, nc, cu, used_str))
                else:
                    if ch in used_str:
                        new_used = used_str
                        new_cu = cu
                    else:
                        new_cu = cu + 1
                        if new_cu > k:
                            continue
                        new_used = ''.join(sorted(set(used_str) | {ch}))
                    new_path = path + ch
                    if new_used not in ha[nr][nc]:
                        heappush(heap, (new_priority, new_path, new_steps, nr, nc, new_cu, new_used))
    return "-1"


class CtrackInteraction(BaseInteraction):
    """Ctrack交互管理器"""
    
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
        score = CtrackRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ctrack问题！"""
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

