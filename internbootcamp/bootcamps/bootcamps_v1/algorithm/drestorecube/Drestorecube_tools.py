import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drestorecube.Drestorecube_reward_calculator import DrestorecubeRewardCalculator

# 导入依赖库
import random
import math
from itertools import permutations
from itertools import product
from itertools import combinations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DrestorecubeVerificationTool(BaseTool):
    """Drestorecube验证工具"""
    
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
            score = DrestorecubeRewardCalculator.verify_score(
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
            logger.error(f"DrestorecubeVerificationTool执行错误: {str(e)}")
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
    def _makes_invalid_cube(self, points):
        """确保points不能组成有效立方体"""
        # 快速初步检查
        if len(points) != 8:
            return True

        # 检查坐标唯一性
        if len(set(map(tuple, points))) < 8:
            return True

        # 计算所有距离的平方
        dists = []
        for (x1, y1, z1), (x2, y2, z2) in combinations(points, 2):
            dists.append((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

        # 有效立方体应有3种不同距离值（边、面对角线、体对角线）
        unique_dists = set(dists)
        if len(unique_dists) != 3:
            return True

        # 检查各距离的数量是否符合立方体特征
        min_dist = min(unique_dists)
        edge_count = dists.count(min_dist)
        return edge_count != 12

    @classmethod
    def check_cube_possible(cls, input_points):
        """实际检查输入是否可能恢复成立方体（用于不可解案例的验证）"""
        # 尝试所有点的排列组合（优化版，仅用于验证生成案例）
        from itertools import permutations

        # 预处理所有可能的顶点排列
        candidates = []
        for pt in input_points:
            candidates.append(set(permutations(pt)))

        # 快速排除明显无效的情况
        unique_points = len(set(map(tuple, input_points)))
        if unique_points < 8:
            return False

        # 随机采样部分排列组合进行验证
        MAX_TRIES = 1000
        for _ in range(MAX_TRIES):
            test_case = [random.choice(list(c)) for c in candidates]
            if cls.is_cube(test_case):
                return True
        return False

    @staticmethod
    def is_cube(points):
        """优化后的几何验证逻辑"""
        # 计算所有点对的平方距离
        dist_counter = {}
        vectors = {}
        for i, j in combinations(range(8), 2):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dz = points[i][2] - points[j][2]
            dist_sq = dx*dx + dy*dy + dz*dz
            dist_counter[dist_sq] = dist_counter.get(dist_sq, 0) + 1
            vectors[(i,j)] = (dx, dy, dz)

        # 有效立方体应有3种距离：边长（min）、面对角线、体对角线
        if len(dist_counter) != 3:
            return False

        # 检查各距离的数量关系
        edges = sorted(dist_counter.keys())
        a2, b2, c2 = edges  # a < b < c
        if dist_counter[a2] != 12 or dist_counter[b2] != 12 or dist_counter[c2] != 4:
            return False

        # 验证平方关系：b^2 = 2a^2，c^2 = 3a^2
        if not (math.isclose(b2, 2*a2, rel_tol=1e-9) and math.isclose(c2, 3*a2, rel_tol=1e-9)):
            return False

        # 验证向量正交性
        edge_vectors = [vec for (i,j), vec in vectors.items() if (points[i][0]-points[j][0])**2 + 
                       (points[i][1]-points[j][1])**2 + (points[i][2]-points[j][2])**2 == a2]

        # 每个边应有三个正交边
        for vec in edge_vectors[:3]:  # 检查前三个边即可
            orthogonal = 0
            for other in edge_vectors:
                if sum(a*b for a, b in zip(vec, other)) == 0:
                    orthogonal += 1
            if orthogonal < 3:
                return False

        return True
