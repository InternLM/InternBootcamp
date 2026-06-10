from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
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


class DpietInteraction(BaseInteraction):
    """Dpiet交互管理器"""
    
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
        score = DpietRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dpiet问题！"""
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
