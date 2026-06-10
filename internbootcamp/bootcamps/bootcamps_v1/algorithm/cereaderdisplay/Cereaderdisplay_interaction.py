from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cereaderdisplay.Cereaderdisplay_reward_calculator import CereaderdisplayRewardCalculator

# 导入依赖库
import random
import re
from typing import List




class CereaderdisplayInteraction(BaseInteraction):
    """Cereaderdisplay交互管理器"""
    
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
        score = CereaderdisplayRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cereaderdisplay问题！"""
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
    def generate_valid_commands(self, n: int) -> List[tuple]:
        """基于参考算法逻辑生成最小命令集合"""
        # 根据题目参考算法逆向生成命令
        commands = []
        # 随机选择对角线操作概率
        if random.random() < 0.3:
            diag_count = random.randint(0, n)
            commands += [(i+1, i+1) for i in random.sample(range(n), diag_count)]

        # 随机生成非对角线操作
        non_diag = [(i+1, j+1) for i in range(n) for j in range(n) if i != j]
        commands += random.sample(non_diag, k=random.randint(0, len(non_diag)))
        return list(set(commands))  # 去重后返回

    def simulate_commands(self, n: int, commands: List[tuple]) -> List[List[int]]:
        """精确模拟命令作用效果"""
        grid = [[0]*n for _ in range(n)]
        for x, y in commands:
            # 处理行x的区域
            start_col = min(x, y) - 1
            end_col = max(x, y) - 1
            for col in range(start_col, end_col + 1):
                if 0 <= col < n:
                    grid[x-1][col] ^= 1

            # 处理列y的区域
            start_row = min(x, y) - 1
            end_row = max(x, y) - 1
            for row in range(start_row, end_row + 1):
                if 0 <= row < n:
                    grid[row][y-1] ^= 1
        return grid

    @staticmethod
    def calculate_min_commands(n: int, grid: List[List[int]]) -> int:
        """完整实现参考算法"""
        a = [[0]*(n+2) for _ in range(n+2)]
        b = [[0]*(n+2) for _ in range(n+2)]
        A = [[0]*(n+2) for _ in range(n+2)]
        B = [[0]*(n+2) for _ in range(n+2)]
        ans = 0

        # 处理右上三角区域
        for J in range(n, 1, -1):
            i, j = 1, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (a[i][j] + b[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    a[i][j-1] = a[i][j] + 1
                    b[i+1][j] = b[i][j] + 1
                else:
                    a[i][j-1] = a[i][j]
                    b[i+1][j] = b[i][j]
                i += 1
                j += 1

        # 处理左下三角区域
        for J in range(2, n+1):
            i, j = n, J
            for _ in range(n - J + 1):
                current_value = grid[i-1][j-1]
                total = (A[i][j] + B[i][j]) % 2

                if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                    ans += 1
                    A[i][j+1] = A[i][j] + 1
                    B[i-1][j] = B[i][j] + 1
                else:
                    A[i][j+1] = A[i][j]
                    B[i-1][j] = B[i][j]
                i -= 1
                j -= 1

        # 处理对角线元素
        for i in range(1, n+1):
            current_value = grid[i-1][i-1]
            total = (a[i][i] + b[i][i] + A[i][i] + B[i][i]) % 2
            if (current_value == 0 and total == 1) or (current_value == 1 and total == 0):
                ans += 1

        return ans
