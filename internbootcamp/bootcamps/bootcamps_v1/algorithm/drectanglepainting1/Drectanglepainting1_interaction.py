from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drectanglepainting1.Drectanglepainting1_reward_calculator import Drectanglepainting1RewardCalculator

# 导入依赖库
import random
import re




class Drectanglepainting1Interaction(BaseInteraction):
    """Drectanglepainting1交互管理器"""
    
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
        score = Drectanglepainting1RewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Drectanglepainting1问题！"""
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
    def compute_min_cost(n, grid):
        # 初始化前缀和数组（从1开始索引）
        f = [[0]*(n+2) for _ in range(n+2)]
        for i in range(1, n+1):
            for j in range(1, n+1):
                cell_value = 1 if grid[i-1][j-1] == '#' else 0
                f[i][j] = f[i-1][j] + f[i][j-1] - f[i-1][j-1] + cell_value

        # 初始化四维DP数组
        d = [[[[0]*(n+2) for _ in range(n+2)] 
             for __ in range(n+2)] 
             for ___ in range(n+2)]

        # 动态规划计算
        for i in range(n, 0, -1):
            for j in range(n, 0, -1):
                for ii in range(i, n+1):
                    for jj in range(j, n+1):
                        # 计算当前区域的黑块总数
                        total = f[ii][jj] - f[i-1][jj] - f[ii][j-1] + f[i-1][j-1]

                        if total == 0:
                            d[i][j][ii][jj] = 0
                            continue

                        # 初始值为区域的最大边长
                        h = ii - i + 1
                        w = jj - j + 1
                        val = max(h, w)

                        # 垂直切分尝试
                        for k in range(j, jj):
                            val = min(val, d[i][j][ii][k] + d[i][k+1][ii][jj])

                        # 水平切分尝试
                        for k in range(i, ii):
                            val = min(val, d[i][j][k][jj] + d[k+1][j][ii][jj])

                        d[i][j][ii][jj] = val

        return d[1][1][n][n]
