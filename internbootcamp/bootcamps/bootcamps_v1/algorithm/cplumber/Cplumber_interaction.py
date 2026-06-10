from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cplumber.Cplumber_reward_calculator import CplumberRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 1000003


class CplumberInteraction(BaseInteraction):
    """Cplumber交互管理器"""
    
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
        score = CplumberRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cplumber问题！"""
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
    def solve_puzzle(n, m, grid):
        ans = 1
        # Row pattern checks
        for row in grid:
            valid_patterns = 0
            # Check two possible row patterns
            for start_with_12 in [False, True]:
                valid = True
                expect_12 = start_with_12
                for c in row:
                    if c == '.': 
                        expect_12 = not expect_12
                        continue
                    if expect_12:
                        if c not in {'1', '2'}:
                            valid = False
                            break
                    else:
                        if c not in {'3', '4'}:
                            valid = False
                            break
                    expect_12 = not expect_12
                if valid:
                    valid_patterns += 1
            ans = (ans * valid_patterns) % MOD

        # Column pattern checks
        for j in range(m):
            valid_patterns = 0
            for start_with_14 in [False, True]:
                valid = True
                expect_14 = start_with_14
                for i in range(n):
                    c = grid[i][j]
                    if c == '.':
                        expect_14 = not expect_14
                        continue
                    if expect_14:
                        if c not in {'1', '4'}:
                            valid = False
                            break
                    else:
                        if c not in {'2', '3'}:
                            valid = False
                            break
                    expect_14 = not expect_14
                if valid:
                    valid_patterns += 1
            ans = (ans * valid_patterns) % MOD
        return ans
