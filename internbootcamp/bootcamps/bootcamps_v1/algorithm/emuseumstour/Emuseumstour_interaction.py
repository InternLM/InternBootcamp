from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.emuseumstour.Emuseumstour_reward_calculator import EmuseumstourRewardCalculator

# 导入依赖库
import random
import re




class EmuseumstourInteraction(BaseInteraction):
    """Emuseumstour交互管理器"""
    
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
        score = EmuseumstourRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Emuseumstour问题！"""
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
    @staticmethod
    def compute_solution(n, m, d, roads, museums):
        """严格实现原题参考算法逻辑"""
        # 邻接表初始化（1-based）
        adj = [[] for _ in range(n+1)]
        rev = [[] for _ in range(n+1)]
        for u, v in roads:
            adj[u].append(v)
            rev[v].append(u)

        # 日期循环处理
        nxt = [(i+1)%d for i in range(d)]
        prev = [(i-1+d)%d for i in range(d)]

        # 第一次DFS确定处理顺序
        visited = [[False]*d for _ in range(n+1)]
        process_stack = []

        for city in range(1, n+1):
            for day in range(d):
                if not visited[city][day]:
                    stack = [(city, day, False)]
                    while stack:
                        x, y, processed = stack.pop()
                        if processed:
                            process_stack.append((x, y))
                            continue
                        if visited[x][y]:
                            continue
                        visited[x][y] = True
                        stack.append((x, y, True))  # 标记为已处理
                        # 处理相邻节点
                        for v in adj[x]:
                            ny = nxt[y]
                            if not visited[v][ny]:
                                stack.append((v, ny, False))

        # 逆向处理强连通分量
        visited = [[False]*d for _ in range(n+1)]
        best = [[0]*d for _ in range(n+1)]
        INIT = 10**9
        best[1][0] = INIT
        max_result = 0

        while process_stack:
            x, y = process_stack.pop()
            if visited[x][y]:
                continue

            component = []
            component_best = 0
            unique_museums = set()
            dfs_stack = [(x, y)]

            # 收集强连通分量节点
            while dfs_stack:
                cx, cy = dfs_stack.pop()
                if visited[cx][cy]:
                    continue
                visited[cx][cy] = True
                component.append((cx, cy))
                component_best = max(component_best, best[cx][cy])

                # 记录未访问的开放博物馆
                if museums[cx-1][cy] == '1' and cx not in unique_museums:
                    unique_museums.add(cx)

                # 逆向遍历
                for u in rev[cx]:
                    py = prev[cy]
                    if not visited[u][py]:
                        dfs_stack.append((u, py))

            # 计算结果
            total = component_best + len(unique_museums)
            for (cx, cy) in component:
                best[cx][cy] = total
                # 更新邻接节点状态
                for v in adj[cx]:
                    nd = nxt[cy]
                    if best[v][nd] < total:
                        best[v][nd] = total
            max_result = max(max_result, total)

        return max_result - INIT
