from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drestorecube.Drestorecube_reward_calculator import DrestorecubeRewardCalculator

# 导入依赖库
import random
import math
from itertools import permutations
from itertools import product
from itertools import combinations




class DrestorecubeInteraction(BaseInteraction):
    """Drestorecube交互管理器"""
    
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
        score = DrestorecubeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Drestorecube问题！"""
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
