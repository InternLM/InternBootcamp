from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccointroubles.Ccointroubles_reward_calculator import CcointroublesRewardCalculator

# 导入依赖库
import random
from collections import deque
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def solve(n, q, t, a_list, constraints):
    """完整实现的解题算法"""
    # 初始化图结构
    g = [[] for _ in range(n+1)]
    in_degree = [0]*(n+1)
    for u, v in constraints:
        g[u].append(v)
        in_degree[v] += 1

    # 拓扑排序检测环
    queue = deque()
    topo_order = []
    for u in range(1, n+1):
        if in_degree[u] == 0:
            queue.append(u)
    
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in g[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    if len(topo_order) != n:
        return 0  # 存在环

    # 计算依赖关系和最小金额
    dep = [0]*(n+1)
    sum_ = [0]*(n+1)
    for u in reversed(topo_order):
        sum_[u] = a_list[u-1]
        max_child_dep = 0
        for v in g[u]:
            sum_[u] += sum_[v]
            if dep[v] > max_child_dep:
                max_child_dep = dep[v]
        dep[u] = max_child_dep + 1

    min_t = sum(a_list[u-1] * dep[u] for u in topo_order)
    if t < min_t:
        return 0

    # 动态规划计算组合数
    target = t - min_t
    dp = [0]*(target+1)
    dp[0] = 1
    for u in topo_order:
        s = sum_[u]
        for j in range(s, target+1):
            dp[j] = (dp[j] + dp[j - s]) % MOD
    
    return dp[target] % MOD if target >=0 else 0


class CcointroublesInteraction(BaseInteraction):
    """Ccointroubles交互管理器"""
    
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
        score = CcointroublesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccointroubles问题！"""
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
    def _calculate_min_t(self, n, a, constraints):
        """辅助函数：计算最小金额"""
        try:
            temp_g = [[] for _ in range(n+1)]
            for u, v in constraints:
                temp_g[u].append(v)

            # 计算拓扑深度
            depth = [0]*(n+1)
            for u in range(n, 0, -1):
                max_child = 0
                for v in temp_g[u]:
                    max_child = max(max_child, depth[v])
                depth[u] = max_child + 1

            return sum(a[u-1] * depth[u] for u in range(1, n+1))
        except:
            return None
