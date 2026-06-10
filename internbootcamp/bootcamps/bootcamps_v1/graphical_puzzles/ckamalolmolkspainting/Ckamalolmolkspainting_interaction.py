from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ckamalolmolkspainting.Ckamalolmolkspainting_reward_calculator import CkamalolmolkspaintingRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n, m, grid):
    a = [[1 if cell == 'X' else 0 for cell in row] for row in grid]
    original_n, original_m = n, m

    def work(a, n, m):
        found = False
        x = y = 0
        for i in range(n):
            for j in range(m):
                if a[i][j]:
                    x, y = i, j
                    found = True
                    break
            if found:
                break
        if not found:
            return n * m * 2  # 无效情况

        lenx = 1
        while x + lenx < n and a[x + lenx][y]:
            lenx += 1

        l = 0
        r = 1
        while y + r < m and a[x][y + r]:
            r += 1
        r += 1  # 初始右边界

        def all_cells(x_check, y_check, lx_check, ly_check):
            if x_check < 0 or y_check < 0 or x_check + lx_check > n or y_check + ly_check > m:
                return False
            for i in range(x_check, x_check + lx_check):
                for j in range(y_check, y_check + ly_check):
                    if not a[i][j]:
                        return False
            return True

        def chk(lx_brush, ly_brush):
            if not all_cells(x, y, lx_brush, ly_brush):
                return 2
            b = [[0] * m for _ in range(n)]
            for i in range(x, x + lx_brush):
                for j in range(y, y + ly_brush):
                    b[i][j] = 1

            current_x, current_y = x, y
            t = 0  # 移动方向标记，0右优先，1下优先
            while True:
                can_right = False
                if current_y + ly_brush < m:
                    can_right = all_cells(current_x, current_y + ly_brush, lx_brush, 1)
                can_down = False
                if current_x + lx_brush < n:
                    can_down = all_cells(current_x + lx_brush, current_y, 1, ly_brush)
                
                if not can_right and not can_down:
                    break

                moved = False
                if can_right and (t == 0 or (not can_down and t == 1)):
                    valid = True
                    for i in range(current_x):
                        if a[i][current_y + ly_brush]:
                            valid = False
                            break
                    if valid:
                        for i in range(current_x, current_x + lx_brush):
                            b[i][current_y + ly_brush] = 1
                        current_y += 1
                        moved = True
                        t = 0
                    else:
                        return 0  # 无效移动路径

                if not moved and can_down and (t == 1 or (not can_right and t == 0)):
                    valid = True
                    for j in range(current_y):
                        if a[current_x + lx_brush][j]:
                            valid = False
                            break
                    if valid:
                        for j in range(current_y, current_y + ly_brush):
                            b[current_x + lx_brush][j] = 1
                        current_x += 1
                        moved = True
                        t = 1
                    else:
                        return 0  # 无效移动路径

                if not moved:
                    break  # 无法移动

            for i in range(n):
                for j in range(m):
                    if a[i][j] != b[i][j]:
                        return 2
            return 1

        left, right = 1, r
        answer = n * m * 2
        while left <= right:
            mid = (left + right) // 2
            res = chk(lenx, mid)
            if res == 1:
                answer = lenx * mid
                right = mid - 1
            elif res == 0:  # 路径无效，需要扩大ly
                left = mid + 1
            else:  # 覆盖不全，需要扩大ly
                left = mid + 1
        return answer if answer <= n * m else n * m * 2

    res1 = work(a, n, m)
    # 转置处理列优先的情况
    a_transposed = [list(row) for row in zip(*a)]
    res2 = work(a_transposed, m, n)
    min_res = min(res1, res2)
    return min_res if min_res <= max(n, m) * max(n, m) else -1


class CkamalolmolkspaintingInteraction(BaseInteraction):
    """Ckamalolmolkspainting交互管理器"""
    
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
        score = CkamalolmolkspaintingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ckamalolmolkspainting问题！"""
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

