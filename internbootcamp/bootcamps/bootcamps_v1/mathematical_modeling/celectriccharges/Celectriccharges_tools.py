import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.celectriccharges.Celectriccharges_reward_calculator import CelectricchargesRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CelectricchargesVerificationTool(BaseTool):
    """Celectriccharges验证工具"""
    
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
            score = CelectricchargesRewardCalculator.verify_score(
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
            logger.error(f"CelectricchargesVerificationTool执行错误: {str(e)}")
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
    def _compute_min_diameter(points):
        # 转换为按x排序的列表，确保与case_generator中的排序一致
        points_sorted = sorted(points, key=lambda p: (p[0], p[1]))
        n = len(points_sorted)
        if n == 0:
            return 0
        if n == 1:
            return 0

        # 预处理前缀和后缀的y的min和max
        pre_min = [0] * n
        pre_max = [0] * n
        pre_min[0] = points_sorted[0][1]
        pre_max[0] = points_sorted[0][1]
        for i in range(1, n):
            pre_min[i] = min(pre_min[i-1], points_sorted[i][1])
            pre_max[i] = max(pre_max[i-1], points_sorted[i][1])

        suf_min = [0] * n
        suf_max = [0] * n
        suf_min[-1] = points_sorted[-1][1]
        suf_max[-1] = points_sorted[-1][1]
        for i in range(n-2, -1, -1):
            suf_min[i] = min(suf_min[i+1], points_sorted[i][1])
            suf_max[i] = max(suf_max[i+1], points_sorted[i][1])

        # 辅助函数计算最大平方距离
        def max_sq_distance(electrons, protons):
            max_sq = 0
            # 电子移动到 (x,0)
            e_points = [(x, 0) for x in electrons]
            # 质子移动到 (0,y)
            p_points = [(0, y) for y in protons]
            all_points = e_points + p_points
            for i in range(len(all_points)):
                for j in range(i, len(all_points)):
                    dx = all_points[i][0] - all_points[j][0]
                    dy = all_points[i][1] - all_points[j][1]
                    sq = dx*dx + dy*dy
                    if sq > max_sq:
                        max_sq = sq
            return max_sq

        # 穷举所有可能的电子和质子的选择组合
        min_sq = float('inf')
        # 优化：对每个点，可以选择电子或质子，但n较大时穷举不适用，但此处假设n较小
        from itertools import product
        for choices in product([0, 1], repeat=n):
            electrons_x = []
            protons_y = []
            for i in range(n):
                if choices[i] == 0:
                    electrons_x.append(points_sorted[i][0])
                else:
                    protons_y.append(points_sorted[i][1])
            current_sq = max_sq_distance(electrons_x, protons_y)
            if current_sq < min_sq:
                min_sq = current_sq
        return min_sq
