from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpropagatingtree.Cpropagatingtree_reward_calculator import CpropagatingtreeRewardCalculator

# 导入依赖库
import random

# === 源文件中的其他类 ===

class FenwickTree:
    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 2)  # 1-based indexing

    def update_point(self, idx, delta):
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def query_prefix(self, idx):
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

    def update_range(self, l, r, delta):
        self.update_point(l, delta)
        self.update_point(r + 1, -delta)


class CpropagatingtreeInteraction(BaseInteraction):
    """Cpropagatingtree交互管理器"""
    
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
        score = CpropagatingtreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpropagatingtree问题！"""
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
    def generate_tree(self, n):
        if n == 1:
            return []
        edges = []
        nodes = [1]
        for i in range(2, n + 1):
            parent = random.choice(nodes)
            edges.append((parent, i))
            nodes.append(i)
        return edges

    def simulate_case(self, case):
        n, a = case['n'], case['a']
        edges, queries = case['edges'], case['queries']
        tree = [[] for _ in range(n + 1)]
        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)

        # Euler Tour初始化
        euler = [-1]
        idx = [0] * (n + 1)
        child = [0] * (n + 1)
        parity = [0] * (n + 1)
        vst = [False] * (n + 1)

        def dfs(u, depth):
            vst[u] = True
            parity[u] = depth % 2
            idx[u] = len(euler)
            euler.append(u)
            child[u] = 1
            for v in tree[u]:
                if not vst[v] and v != u:
                    dfs(v, depth + 1)
                    child[u] += child[v]

        dfs(1, 0)
        max_size = len(euler) - 1

        # 初始化两个BIT
        bit0 = FenwickTree(max_size)
        bit1 = FenwickTree(max_size)
        expected = []

        # 处理查询
        for query in queries:
            if query[0] == '1':
                x = int(query[1])
                val = int(query[2])
                p = parity[x]
                L = idx[x]
                R = L + child[x] - 1  # 闭区间

                if p == 0:
                    bit0.update_range(L, R, val)
                    bit1.update_range(L, R, -val)
                else:
                    bit1.update_range(L, R, val)
                    bit0.update_range(L, R, -val)
            else:
                x = int(query[1])
                p = parity[x]
                sum_p = bit0.query_prefix(idx[x]) if p == 0 else bit1.query_prefix(idx[x])
                expected.append(a[x-1] + sum_p)
        return expected
