import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.maze_reward_calculator import MazeRewardCalculator

# 导入依赖库
import ast
import json
import random
import re
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_generator import generate_maze
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_solver import solve_maze
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_solver import is_path_exist
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.maze.lib.maze_validator import validate_maze_solution

# === 源文件中的全局函数 ===

def unit_test(size):
     ## Unit test
    maze_bootcamp = Mazebootcamp(size=size, difficulty=1)
    identity = maze_bootcamp.case_generator()
    print(maze_bootcamp.prompt_func(identity))
    solution = solve_maze(identity['grid'], identity['start_pos'], identity['end_pos'])[0]
    fake_output = f"""\n略，
    Final-answer: ```json
    {solution}
    ```"""
    print(fake_output)
    print("Is it correct? ",maze_bootcamp.verify_score(fake_output, identity))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class MazeVerificationTool(BaseTool):
    """Maze验证工具"""
    
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
            score = MazeRewardCalculator.verify_score(
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
            logger.error(f"MazeVerificationTool执行错误: {str(e)}")
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
    def print_maze_str(identity: dict):
        """返回迷宫的字符串表示"""
        if identity['grid'] is None:
            return "没有迷宫可显示"

        result = "Maze:\n"
        for i, row in enumerate(identity['grid']):
            line = ""
            for j, cell in enumerate(row):
                if (i, j) == identity['start_pos']:
                    line += "S "  # 起点
                elif (i, j) == identity['end_pos']:
                    line += "E "  # 终点
                elif cell == 0:
                    line += "P "  # 通路
                else:
                    line += "W "  # 墙
            result += line + "\n"
        return result
