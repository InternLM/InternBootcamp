from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eonchangingtree.Eonchangingtree_reward_calculator import EonchangingtreeRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

mod = 10**9 + 7



# === 源文件中的全局函数 ===

def build_adj(parents, n):
    adj = {i: [] for i in range(1, n+1)}
    for i in range(2, n+1):
        parent = parents[i-2]
        adj[parent].append(i)
    return adj

def dfs(x, parent_adj, tin, tout, dep, current_time, current_g):
    current_time[0] += 1
    tin[x] = current_time[0]
    dep[tin[x]] = current_g
    for child in parent_adj.get(x, []):
        dfs(child, parent_adj, tin, tout, dep, current_time, current_g-1)
    tout[x] = current_time[0]

def perform_dfs(n, parent_adj):
    tin = [0] * (n + 1)
    tout = [0] * (n + 1)
    dep = [0] * (n + 2)  # tin values are 1-based
    current_time = [0]
    dfs(1, parent_adj, tin, tout, dep, current_time, n)
    return tin, tout, dep

def process_queries_for_identity(queries, n, tin_dict, tout_dict, dep_list):
    a = [0] * (n + 2)
    b = [0] * (n + 2)
    expected_outputs = []
    for query in queries:
        if query['type'] == 1:
            v = query['v']
            x = query['x']
            k = query['k']
            tin_v = tin_dict[v]
            tout_v = tout_dict[v]
            f1 = (x - dep_list[tin_v] * k) % mod
            f2 = k % mod
            for u in range(1, n+1):
                u_tin = tin_dict[u]
                if tin_v <= u_tin <= tout_v:
                    a[u_tin] = (a[u_tin] + f1) % mod
                    b[u_tin] = (b[u_tin] + f2) % mod
        else:
            v = query['v']
            u_tin = tin_dict[v]
            res = (a[u_tin] + b[u_tin] * dep_list[u_tin]) % mod
            expected_outputs.append(res)
    return expected_outputs


class EonchangingtreeInteraction(BaseInteraction):
    """Eonchangingtree交互管理器"""
    
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
        score = EonchangingtreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eonchangingtree问题！"""
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

