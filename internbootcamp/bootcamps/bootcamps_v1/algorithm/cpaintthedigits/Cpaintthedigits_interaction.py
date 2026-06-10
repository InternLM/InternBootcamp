from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpaintthedigits.Cpaintthedigits_reward_calculator import CpaintthedigitsRewardCalculator

# 导入依赖库
import random
import re




class CpaintthedigitsInteraction(BaseInteraction):
    """Cpaintthedigits交互管理器"""
    
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
        score = CpaintthedigitsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpaintthedigits问题！"""
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
    def generate_non_decreasing(self, length):
        if length == 0:
            return []
        sequence = [random.randint(0, 9)]
        for _ in range(length-1):
            sequence.append(random.randint(sequence[-1], 9))
        return sequence

    @staticmethod
    def solve(N, A):
        B = ['1'] * N
        last_1 = -1
        transition_point = None
        last_2 = -1

        for i in range(N):
            current = A[i]

            if last_1 == -1:
                last_1 = current
                continue

            if current >= last_1:
                last_1 = current
                continue

            if transition_point is None:
                # Find transition point
                transition_point = i
                min_2_val = current
                for m in range(current + 1, 10):
                    for j in range(i):
                        if A[j] == m and B[j] == '1':
                            transition_point = j
                            min_2_val = m
                            break
                    else:
                        continue
                    break
                else:
                    return '-'

                # Update colors for transition segment
                for j in range(transition_point):
                    if A[j] >= min_2_val:
                        B[j] = '2'
                last_2 = max(A[transition_point:i], default=-1)
                last_1 = current
            else:
                if current < last_1 or (current > last_2 and last_2 != -1):
                    return '-'
                if current >= last_2:
                    B[i] = '2'
                    last_2 = current
                else:
                    last_1 = current
        return ''.join(B)
