from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.binvarianceoftree.Binvarianceoftree_reward_calculator import BinvarianceoftreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def check_permutation_solution(n, p_list_1based):
    if n == 0:
        return (False, [])
    p_list = [x - 1 for x in p_list_1based]  # Convert to 0-based
    was = [False] * n
    cyc = defaultdict(list)

    # Find all cycles
    for i in range(n):
        if was[i]:
            continue
        cycle = []
        j = i
        while not was[j]:
            was[j] = True
            cycle.append(j)
            j = p_list[j]
        cyc[len(cycle)].append(cycle)
    
    lengths = sorted(cyc.keys(), reverse=True)
    parent = {}
    roots = []
    
    # Determine parents for each cycle length
    for l in lengths:
        found = False
        for m in lengths:
            if m < l and l % m == 0:
                parent[l] = m
                found = True
                break
        if not found:
            parent[l] = None
            roots.append(l)
    
    # Check validity of roots
    if len(roots) > 1 or (len(roots) == 1 and roots[0] > 2):
        return (False, None)
    
    # Construct the tree edges
    edges = []
    if roots:
        root_len = roots[0]
    else:
        return (False, None)
    
    # Handle root cycle(s)
    if root_len == 2:
        root_cycle = cyc[2][0]
        edges.append((root_cycle[0], root_cycle[1]))
        for cycle in cyc[2][1:]:
            edges.append((root_cycle[0], cycle[0]))
            edges.append((root_cycle[1], cycle[1]))
    elif root_len == 1 and 1 in cyc:
        main_node = cyc[1][0][0]
        for cycle in cyc[1][1:]:
            edges.append((main_node, cycle[0]))
    
    # Attach other cycles to their parents
    for l in lengths:
        if l == root_len:
            continue
        if l not in parent:
            continue
        parent_len = parent[l]
        if parent_len is None:
            continue
        parent_cycles = cyc[parent_len]
        for cycle in cyc[l]:
            for i in range(len(cycle)):
                parent_node = parent_cycles[0][i % parent_len]
                edges.append((parent_node, cycle[i]))
    
    # Convert edges back to 1-based
    edges_1based = [(u + 1, v + 1) for u, v in edges]
    return (True, edges_1based)


class BinvarianceoftreeInteraction(BaseInteraction):
    """Binvarianceoftree交互管理器"""
    
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
        score = BinvarianceoftreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Binvarianceoftree问题！"""
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

