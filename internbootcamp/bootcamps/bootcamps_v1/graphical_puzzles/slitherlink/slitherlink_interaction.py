from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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




class SlitherlinkInteraction(BaseInteraction):
    """Slitherlink交互管理器"""
    
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
        score = SlitherlinkRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个slitherlink问题！"""
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
