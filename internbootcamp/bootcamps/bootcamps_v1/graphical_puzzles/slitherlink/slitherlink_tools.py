import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.slitherlink.slitherlink_reward_calculator import SlitherlinkRewardCalculator

# 导入依赖库
import ast
import json
import random
import re
from typing import Dict
from typing import List
from typing import Any
from typing import Tuple
from typing import Optional
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.slitherlink.lib.slitherlink_generator import SlitherlinkSolver
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.slitherlink.lib.slitherlink_generator import generate_puzzle



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class SlitherlinkVerificationTool(BaseTool):
    """Slitherlink验证工具"""
    
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
            score = SlitherlinkRewardCalculator.verify_score(
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
            logger.error(f"SlitherlinkVerificationTool执行错误: {str(e)}")
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
    def print_puzzle_str(identity: Dict[str, Any]) -> str:
        """
        返回谜题的字符串表示

        Args:
            identity: 包含谜题信息的字典

        Returns:
            谜题的字符串表示
        """
        if identity.get('grid') is None:
            return "没有谜题可显示"

        result = "Slitherlink谜题:\n"
        for row in identity['grid']:
            line = ""
            for cell in row:
                line += str(cell) if cell is not None else "."
            result += line + "\n"
        return result

    @staticmethod
    def visualize_solution(identity: Dict[str, Any], solution: List[int]) -> str:
        """
        可视化解决方案

        Args:
            identity: 包含谜题信息的字典
            solution: 解决方案（边的列表）

        Returns:
            解决方案的可视化字符串
        """
        rows, cols = identity['size']
        grid = identity['grid']

        # 创建点的网格 (rows+1) x (cols+1)
        points = [['.' for _ in range(cols + 1)] for _ in range(rows + 1)]

        # 创建水平边和垂直边的网格
        h_edges = [[' ' for _ in range(cols)] for _ in range(rows + 1)]
        v_edges = [[' ' for _ in range(cols + 1)] for _ in range(rows)]

        # 填充解决方案中的边
        for edge in solution:
            edge = edge - 1  # 调整索引（假设边从1开始编号）
            vert_edges = rows * (cols + 1)

            if edge < vert_edges:
                # 垂直边
                edge_row = edge // (cols + 1)
                edge_col = edge % (cols + 1)
                v_edges[edge_row][edge_col] = '|'
            else:
                # 水平边
                edge -= vert_edges
                edge_row = edge // cols
                edge_col = edge % cols
                h_edges[edge_row][edge_col] = '-'

        # 生成可视化输出
        result = "解决方案:\n"
        for i in range(rows + 1):
            # 打印水平边
            h_line = ""
            for j in range(cols + 1):
                h_line += points[i][j]
                if j < cols:
                    h_line += h_edges[i][j]
            result += h_line + "\n"

            # 打印垂直边和数字
            if i < rows:
                v_line = ""
                for j in range(cols + 1):
                    v_line += v_edges[i][j]
                    if j < cols:
                        cell_value = grid[i][j]
                        v_line += str(cell_value) if cell_value is not None else " "
                result += v_line + "\n"

        return result
