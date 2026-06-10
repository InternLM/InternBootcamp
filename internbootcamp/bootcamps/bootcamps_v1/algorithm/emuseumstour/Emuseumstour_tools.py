import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.emuseumstour.Emuseumstour_reward_calculator import EmuseumstourRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EmuseumstourVerificationTool(BaseTool):
    """Emuseumstour验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = EmuseumstourRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"EmuseumstourVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
