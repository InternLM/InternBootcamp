from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dmisspunyverse.Dmisspunyverse_reward_calculator import DmisspunyverseRewardCalculator

# 导入依赖库
import random
from sys import setrecursionlimit




class DmisspunyverseInteraction(BaseInteraction):
    """Dmisspunyverse交互管理器"""
    
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
        score = DmisspunyverseRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dmisspunyverse问题！"""
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
    def generate_tree_edges(self, n):
        """生成合法的树结构，节点编号从1开始"""
        if n == 1:
            return []
        edges = []
        parents = list(range(n))
        for i in range(1, n):
            parents[i] = random.randint(0, i-1)
        # 转换为1-based节点编号
        for i in range(1, n):
            u = parents[i] + 1
            v = i + 1
            edges.append((u, v))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_case(n, m, b, w, edges):
        """树形DP实现，修复状态初始化问题"""
        # 构建邻接表 (0-based)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u-1].append(v-1)
            adj[v-1].append(u-1)

        a = [w[i] - b[i] for i in range(n)]

        # DP状态数组 (max_m+2防止越界)
        max_m = m
        dp = [[(-1, -float('inf'))] * (max_m + 2) for _ in range(n)]
        sz = [0] * n

        def dfs(parent, u):
            sz[u] = 1
            dp[u][1] = (0, a[u])  # 初始状态

            for v in adj[u]:
                if v == parent:
                    continue
                dfs(u, v)

                # 合并子树状态
                current_max = min(sz[u], max_m)
                child_max = min(sz[v], max_m)
                ndp = [(-1, -float('inf'))] * (current_max + child_max + 1)

                for i in range(1, current_max + 1):
                    if dp[u][i][0] == -1:
                        continue
                    for j in range(1, child_max + 1):
                        if dp[v][j][0] == -1:
                            continue

                        # 合并分支选项
                        merged_k = i + j - 1
                        if merged_k <= max_m:
                            total_win = dp[u][i][0] + dp[v][j][0]
                            total_sum = dp[u][i][1] + dp[v][j][1]
                            if (total_win > ndp[merged_k][0]) or \
                               (total_win == ndp[merged_k][0] and total_sum > ndp[merged_k][1]):
                                ndp[merged_k] = (total_win, total_sum)

                        # 独立分支选项
                        separate_k = i + j
                        if separate_k <= max_m:
                            add_win = 1 if dp[v][j][1] > 0 else 0
                            total_win = dp[u][i][0] + dp[v][j][0] + add_win
                            total_sum = dp[u][i][1]
                            if (total_win > ndp[separate_k][0]) or \
                               (total_win == ndp[separate_k][0] and total_sum > ndp[separate_k][1]):
                                ndp[separate_k] = (total_win, total_sum)

                # 更新状态数组
                for k in range(len(ndp)):
                    if k > max_m:
                        continue
                    if ndp[k][0] > dp[u][k][0] or \
                       (ndp[k][0] == dp[u][k][0] and ndp[k][1] > dp[u][k][1]):
                        dp[u][k] = ndp[k]
                sz[u] += sz[v]

        dfs(-1, 0)
        max_win, sum_total = dp[0][m]

        # 处理根节点的剩余值
        if sum_total > 0:
            max_win += 1
        return max(max_win, 0)  # 保证非负
