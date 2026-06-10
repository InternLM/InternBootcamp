from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eteambuilding.Eteambuilding_reward_calculator import EteambuildingRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_correct_answer(n, m, k, c_list, edges):
    group_edges = defaultdict(list)
    cross_edges = []
    mark = defaultdict(bool)
    
    # 学生编号1-based处理
    c = [0] * (n + 1)
    for i in range(1, n+1):
        c[i] = c_list[i-1]
    
    dsu = DSU(2*(n+2))  # 每个节点分拆为两个
    
    # 分离同组边和跨组边
    for a, b in edges:
        if c[a] == c[b]:
            group_edges[c[a]].append((a, b))
        else:
            u, v = sorted([c[a], c[b]])
            cross_edges.append((u, v, a, b))
    
    # 处理同组边（标记矛盾组）
    for group in group_edges:
        conflict = False
        cp = len(dsu.history)
        for a, b in group_edges[group]:
            # 检查合并是否产生矛盾
            dsu.merge(a, b + n)
            dsu.merge(b, a + n)
            if dsu.find(a) == dsu.find(a + n):
                conflict = True
                break
        if conflict:
            mark[group] = True
        dsu.rollback(cp)  # 回滚到处理前的状态
    
    # 排序跨组边（关键修正点）
    cross_edges.sort(key=lambda x: (x[0], x[1]))
    
    # 统计无效组对
    total_pairs = k * (k - 1) // 2
    invalid_pairs = 0
    tot_marked = sum(mark.values())
    invalid_pairs += tot_marked * (k - tot_marked) + tot_marked * (tot_marked - 1) // 2
    
    # 处理跨组边（修正排序逻辑）
    i = 0
    while i < len(cross_edges):
        j = i
        current_u = cross_edges[i][0]
        current_v = cross_edges[i][1]
        while j < len(cross_edges) and cross_edges[j][0:2] == (current_u, current_v):
            j += 1
        
        if mark[current_u] or mark[current_v]:
            invalid_pairs += 1
            i = j
            continue
        
        conflict = False
        cp = len(dsu.history)
        for idx in range(i, j):
            _, _, a, b = cross_edges[idx]
            dsu.merge(a, b + n)
            dsu.merge(b, a + n)
            if dsu.find(a) == dsu.find(a + n) or dsu.find(b) == dsu.find(b + n):
                conflict = True
                break
        
        if conflict:
            invalid_pairs += 1
        dsu.rollback(cp)
        i = j
    
    return total_pairs - invalid_pairs



# === 源文件中的其他类 ===

class DSU:
    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size
        self.history = []
    
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # 路径压缩
            x = self.parent[x]
        return x
    
    def merge(self, x, y):
        fx = self.find(x)
        fy = self.find(y)
        if fx == fy:
            return
        if self.size[fx] < self.size[fy]:
            fx, fy = fy, fx
        self.history.append((fy, fx))  # 记录合并顺序
        self.parent[fy] = fx
        self.size[fx] += self.size[fy]
    
    def rollback(self, checkpoint):
        while len(self.history) > checkpoint:
            fy, fx = self.history.pop()
            self.parent[fy] = fy
            self.size[fx] -= self.size[fy]


class EteambuildingInteraction(BaseInteraction):
    """Eteambuilding交互管理器"""
    
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
        score = EteambuildingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eteambuilding问题！"""
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

