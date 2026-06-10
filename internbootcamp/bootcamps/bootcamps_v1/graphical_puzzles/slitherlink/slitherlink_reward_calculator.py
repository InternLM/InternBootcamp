import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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




class SlitherlinkRewardCalculator(BaseRewardCalculator):
    """Slitherlink奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> List[int]:
        """
        从模型输出中提取解答

        Args:
            output: 模型输出的文本

        Returns:
            边的列表
        """
        pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, output)
        if matches:
            python_str = matches[-1]
            try:
                # 尝试解析为Python对象
                result = ast.literal_eval(python_str.strip())
                if isinstance(result, list):
                    return result
                return []
            except Exception:
                # 如果解析失败，尝试查找数字列表
                number_pattern = r'\[([0-9, ]+)\]'
                number_matches = re.findall(number_pattern, python_str)
                if number_matches:
                    try:
                        return [int(x.strip()) for x in number_matches[0].split(',')]
                    except:
                        return []
        return []
    
    @classmethod
    def _verify_correction(cls, solution: List[int], identity: Dict[str, Any]) -> bool:
        """
        验证解决方案是否正确

        Args:
            solution: 解决方案（边的列表）
            identity: 包含谜题信息的字典

        Returns:
            解决方案是否正确
        """
        if not solution:
            return False

        solver = SlitherlinkSolver()
        solver.cells = identity['grid']
        solver.height = identity['size'][0]
        solver.width = identity['size'][1]

        # 验证单元格约束
        for row in range(solver.height):
            for col in range(solver.width):
                cell_value = solver.cells[row][col]
                if cell_value is not None:
                    # 获取单元格周围的边
                    cell_id = row * solver.width + col
                    edges = solver.get_cell_edges(cell_id)

                    # 计算解决方案中包含的边数
                    edge_count = sum(1 for edge in edges if edge + 1 in solution)

                    # 验证边数是否与单元格值匹配
                    if edge_count != cell_value:
                        return False

        # 验证是否形成有效的闭环
        return solver.validate(solution)
    
    # 其他额外方法

