from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.unknown.epainttree.Epainttree_reward_calculator import EpainttreeRewardCalculator

# 导入依赖库
import random
import functools
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_random_tree_edges(n):
    if n == 1:
        return []
    if n == 2:
        return [(1, 2)]
    prufer = [random.randint(1, n) for _ in range(n-2)]
    degree = defaultdict(int)
    for node in prufer:
        degree[node] += 1
    leaves = []
    for v in range(1, n+1):
        if degree[v] == 0:
            leaves.append(v)
    edges = []
    for node in prufer:
        leaf = leaves.pop(0)
        edges.append((leaf, node))
        degree[leaf] -= 1
        degree[node] -= 1
        if degree[node] == 0:
            leaves.append(node)
        leaves.sort()
    edges.append((leaves[0], leaves[1]))
    edges = [tuple(sorted(e)) for e in edges]
    return edges[:n-1]

def generate_points(n, min_coord=-10**9, max_coord=10**9):
    xs = random.sample(range(min_coord, max_coord + 1), n)
    ys = [x**2 + random.randint(-1000, 1000) for x in xs]
    return list(zip(xs, ys))

def generate_solution(n, edges, points):
    g = [[] for _ in range(n)]
    for u, v in edges:
        u0 = u - 1
        v0 = v - 1
        g[u0].append(v0)
        g[v0].append(u0)
    p_list = [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(points)]
    size = [1] * n

    def dfs(v, parent):
        total = 1
        for to in g[v]:
            if to != parent:
                total += dfs(to, v)
        size[v] = total
        return total
    dfs(0, -1)
    sorted_p = sorted(p_list, key=lambda pt: (-pt['y'], pt['x']))
    ans = [0] * n

    def rec(v, pts, parent):
        if not pts:
            return
        current = pts[0]
        ans[current['id']] = v
        remaining = pts[1:]
        if not remaining:
            return
        gx, gy = current['x'], current['y']
        def compare(a, b):
            val = (a['x'] - gx) * (b['y'] - gy) - (b['x'] - gx) * (a['y'] - gy)
            return -1 if val > 0 else 1 if val < 0 else 0
        remaining_sorted = sorted(remaining, key=functools.cmp_to_key(compare))
        cur = 0
        for to in g[v]:
            if to != parent:
                subset = remaining_sorted[cur:cur + size[to]]
                cur += size[to]
                rec(to, subset, v)
    rec(0, sorted_p, -1)
    return [ans[i] + 1 for i in range(n)]

def segments_intersect(a, b, c, d):
    def ccw(A, B, C):
        return (B[0]-A[0])*(C[1]-A[1]) - (B[1]-A[1])*(C[0]-A[0])
    ccw1 = ccw(a, b, c)
    ccw2 = ccw(a, b, d)
    ccw3 = ccw(c, d, a)
    ccw4 = ccw(c, d, b)
    
    if (ccw1 * ccw2 < 0) and (ccw3 * ccw4 < 0):
        return True
    
    def on_segment(p, a, b):
        return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and \
               (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) and \
               (ccw(a, b, p) == 0)
    
    return on_segment(c, a, b) or on_segment(d, a, b) or \
           on_segment(a, c, d) or on_segment(b, c, d)


class EpainttreeInteraction(BaseInteraction):
    """Epainttree交互管理器"""
    
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
        score = EpainttreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Epainttree问题！"""
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

