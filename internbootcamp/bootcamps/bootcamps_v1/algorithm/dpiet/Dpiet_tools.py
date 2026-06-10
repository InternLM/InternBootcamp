import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dpiet.Dpiet_reward_calculator import DpietRewardCalculator

# 导入依赖库
import random
import re
from collections import deque

# === 源文件中的其他类 ===

class DpietSimulator:
    DIRS = [{'x':0,'y':-1}, {'x':1,'y':0}, {'x':0,'y':1}, {'x':-1,'y':0}]  # 上下左右
    
    def __init__(self, m, n, pixels):
        self.m = m
        self.n = n
        self.pixels = pixels
        self.cols = len(pixels[0])
        self.bp = {'x':0, 'y':0}
        self.dp = 1  # 初始方向：右
        self.cp = 0  # 初始选择器：左
    
    def simulate(self):
        history = []
        colors = []
        
        for _ in range(self.n):
            # 循环检测
            state = (self.bp['x'], self.bp['y'], self.dp, self.cp)
            if state in history:
                idx = history.index(state)
                cycle = colors[idx:]
                return cycle[(self.n - idx) % len(cycle)]
            history.append(state)
            
            # 步骤1：移动到DP方向边缘
            self.move_to_edge(self.dp)
            # 步骤2：移动到CP方向边缘
            self.move_to_edge(self.cp)
            
            # 步骤3：尝试移动
            next_x = self.bp['x'] + self.DIRS[self.dp]['x']
            next_y = self.bp['y'] + self.DIRS[self.dp]['y']
            
            if self.is_out_of_bounds(next_x, next_y) or self.pixels[next_y][next_x] == '0':
                # 处理方向调整
                if self.cp == (self.dp - 1) % 4:
                    self.cp = (self.cp + 2) % 4
                else:
                    self.dp = (self.dp + 1) % 4
                    self.cp = (self.dp - 1) % 4
            else:
                self.bp = {'x': next_x, 'y': next_y}
            
            colors.append(self.pixels[self.bp['y']][self.bp['x']])
        
        return colors[-1]

    def move_to_edge(self, direction):
        current_color = self.pixels[self.bp['y']][self.bp['x']]
        while True:
            next_x = self.bp['x'] + self.DIRS[direction]['x']
            next_y = self.bp['y'] + self.DIRS[direction]['y']
            if self.is_out_of_bounds(next_x, next_y):
                break
            if self.pixels[next_y][next_x] != current_color:
                break
            self.bp = {'x': next_x, 'y': next_y}
    
    def is_out_of_bounds(self, x, y):
        return not (0 <= x < self.cols and 0 <= y < self.m)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DpietVerificationTool(BaseTool):
    """Dpiet验证工具"""
    
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
            score = DpietRewardCalculator.verify_score(
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
            logger.error(f"DpietVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_piet_grid(self, m, cols):
        grid = [['0']*cols for _ in range(m)]
        colors = deque(random.sample('123456789', k=9))
        visited = [[False]*cols for _ in range(m)]

        # 生成初始块（包含(0,0)）
        color = colors.popleft()
        max_h = min(random.randint(1, m), m)
        max_w = min(random.randint(1, cols), cols)
        for i in range(max_h):
            for j in range(max_w):
                grid[i][j] = color
                visited[i][j] = True

        # 生成后续色块
        while colors:
            candidates = []
            for i in range(m):
                for j in range(cols):
                    if not visited[i][j]:
                        if (i == 0 or visited[i-1][j]) and (j == 0 or visited[i][j-1]):
                            max_h_block = 1
                            while i+max_h_block < m and not visited[i+max_h_block][j]:
                                max_h_block += 1
                            max_w_block = 1
                            while j+max_w_block < cols and not visited[i][j+max_w_block]:
                                max_w_block += 1
                            if max_h_block >=1 and max_w_block >=1:
                                candidates.append((i,j,max_h_block,max_w_block))

            if not candidates:
                break

            i,j,h_max,w_max = random.choice(candidates)
            color = colors.popleft()
            h = random.randint(1, h_max)
            w = random.randint(1, w_max)

            for di in range(h):
                for dj in range(w):
                    if i+di < m and j+dj < cols:
                        grid[i+di][j+dj] = color
                        visited[i+di][j+dj] = True

        return [''.join(row) for row in grid]

    @staticmethod
    def _simulate_piet(m, n, pixels):
        simulator = DpietSimulator(m, n, pixels)
        return simulator.simulate()
