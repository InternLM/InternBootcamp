import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fbreakup.Fbreakup_reward_calculator import FbreakupRewardCalculator

# 导入依赖库
import random
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FbreakupVerificationTool(BaseTool):
    """Fbreakup验证工具"""
    
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
            score = FbreakupRewardCalculator.verify_score(
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
            logger.error(f"FbreakupVerificationTool执行错误: {str(e)}")
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
    def _generate_single_case(self):
        """生成需要切断一条边的案例（链式结构）"""
        n = random.randint(self.min_nodes, self.max_nodes)
        s, t = 1, n
        roads = []
        for i in range(n-1):
            w = random.randint(self.min_budget, self.max_budget)
            roads.append( (i+1, i+2, w) )

        # 找预算最小的边
        min_idx, (x,y,min_w) = min(enumerate(roads), key=lambda x: x[1][2])
        return {
            'n': n,
            'm': n-1,
            's': s,
            't': t,
            'roads': roads,
            'expected': {
                'min_budget': min_w,
                'c': 1,
                'roads': [min_idx+1]  # 道路编号从1开始
            }
        }

    def _generate_double_case(self):
        """生成需要切断两条边的案例（并行双路径结构）"""
        # s=1, t=4
        roads = [
            (1,2, random.randint(10,50)),  # 路径1-边1
            (2,4, random.randint(10,50)),  # 路径1-边2
            (1,3, random.randint(10,50)),  # 路径2-边1
            (3,4, random.randint(10,50)),  # 路径2-边2
            (2,3, self.max_budget*2)       # 高成本边，不应被选
        ]
        # 最优解为选两条路径各一个最低成本边
        path1 = [roads[0][2], roads[1][2]]
        path2 = [roads[2][2], roads[3][2]]
        min1 = min(path1)
        min2 = min(path2)
        solution = {
            'min_budget': min1 + min2,
            'c': 2,
            'roads': [
                roads.index(r)+1 for r in roads 
                if r[2] in (min1, min2)
            ]
        }
        return {
            'n': 4,
            'm': 5,
            's': 1,
            't': 4,
            'roads': roads,
            'expected': solution
        }

    def _generate_impossible_case(self):
        """生成无法断开连接的案例"""
        return {
            'n': 3,
            'm': 4,
            's': 1,
            't': 3,
            'roads': [
                (1,2, 10), (2,3, 20),
                (1,3, 30), (1,3, 40)
            ],
            'expected': -1
        }

    @staticmethod
    def _is_disconnected(n, roads, s, t, deleted_roads):
        """判断删除指定边后是否断开连接"""
        deleted = set(deleted_roads)
        adj = [[] for _ in range(n+1)]
        for idx, (x,y,w) in enumerate(roads):
            if (idx+1) not in deleted:
                adj[x].append(y)
                adj[y].append(x)

        # BFS检查连通性
        visited = [False]*(n+1)
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            if u == t:
                return False
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        return True
