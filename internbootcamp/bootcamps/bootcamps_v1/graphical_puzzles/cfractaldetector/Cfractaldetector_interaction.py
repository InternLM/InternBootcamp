from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cfractaldetector.Cfractaldetector_reward_calculator import CfractaldetectorRewardCalculator

# 导入依赖库
import random
import re




class CfractaldetectorInteraction(BaseInteraction):
    """Cfractaldetector交互管理器"""
    
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
        score = CfractaldetectorRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cfractaldetector问题！"""
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
    def generate_fractal(mask, steps):
        size = 2 ** (steps + 1)
        grid = [['.' for _ in range(size)] for _ in range(size)]
        kx = [0, 0, 1, 1]
        ky = [0, 1, 0, 1]

        def fill(x, y, block_size, current_step, is_black):
            if current_step > steps:
                for i in range(x, x + block_size):
                    for j in range(y, y + block_size):
                        grid[i][j] = '*' if is_black else '.'
                return

            new_size = block_size // 2
            for q in range(4):
                dx = kx[q] * new_size
                dy = ky[q] * new_size
                nx = x + dx
                ny = y + dy
                if is_black:
                    fill(nx, ny, new_size, current_step + 1, True)
                else:
                    bit = (mask >> (3 - q)) & 1
                    sub_black = bit == 1
                    fill(nx, ny, new_size, current_step + 1, sub_black)

        fill(0, 0, size, 0, False)
        return grid

    @staticmethod
    def count_valid_fractals(grid):
        n, m = len(grid), len(grid[0]) if grid else 0
        if n < 8 or m < 8:
            return 0

        # 修正二维前缀和计算
        sum_ = [[0]*(m+1) for _ in range(n+1)]
        for i in range(1, n+1):
            for j in range(1, m+1):
                sum_[i][j] = sum_[i-1][j] + sum_[i][j-1] - sum_[i-1][j-1] + (1 if grid[i-1][j-1] == '*' else 0)

        MAX_ST = 10
        K = 16
        # 调整DP数组维度顺序
        dp = [[[[False]*m for _ in range(n)] for __ in range(K)] for ___ in range(MAX_ST)]

        # 初始化st=0的状态
        for i in range(n):
            for j in range(m):
                for mask in range(K):
                    dp[0][mask][i][j] = (grid[i][j] == '.')

        # 动态规划状态转移
        for st in range(1, MAX_ST):
            w = 1 << (st-1)
            if 2*w > min(n, m):
                continue
            for mask in range(K):
                for i in range(n - 2*w +1):
                    for j in range(m - 2*w +1):
                        valid = True
                        for q in range(4):
                            x = i + (q//2)*w
                            y = j + (q%2)*w
                            if (mask >> (3-q)) & 1:  # 检查当前象限是否需要全黑
                                # 计算区域全黑的正确公式
                                a, b = x+1, y+1
                                c, d = x + w, y + w
                                total = sum_[c][d] - sum_[a-1][d] - sum_[c][b-1] + sum_[a-1][b-1]
                                if total != w*w:
                                    valid = False
                                    break
                            else:
                                if x >=n or y >=m or not dp[st-1][mask][x][y]:
                                    valid = False
                                    break
                        dp[st][mask][i][j] = valid

        # 统计有效解
        count = 0
        for st in range(2, MAX_ST):
            w = 1 << st
            if 2*w > min(n, m):
                continue
            for i in range(n - 2*w +1):
                for j in range(m - 2*w +1):
                    for mask in range(K):
                        if dp[st][mask][i][j]:
                            count +=1
        return count
