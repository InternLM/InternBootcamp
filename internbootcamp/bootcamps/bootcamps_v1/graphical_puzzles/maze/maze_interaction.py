from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class MazeInteraction(BaseInteraction):
    """Maze交互管理器"""
    
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
        score = MazeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个maze问题！"""
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
