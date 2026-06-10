import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EteambuildingVerificationTool(BaseTool):
    """Eteambuilding验证工具"""
    
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
            score = EteambuildingRewardCalculator.verify_score(
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
            logger.error(f"EteambuildingVerificationTool执行错误: {str(e)}")
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

