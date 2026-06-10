from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpetyaandspiders.Cpetyaandspiders_reward_calculator import CpetyaandspidersRewardCalculator

# 导入依赖库
import random
import re




class CpetyaandspidersInteraction(BaseInteraction):
    """Cpetyaandspiders交互管理器"""
    
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
        score = CpetyaandspidersRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpetyaandspiders问题！"""
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
    def __compute_f(self, n, m):
        """
        计算函数f(n, m)的值，用于确定最少蜘蛛数。
        """
        if n < m:
            return self.__compute_f(m, n)
        if m == 1:
            return (n + 2) // 3
        elif m == 2:
            return (n + 2) // 2
        elif m == 3:
            return (3 * n + 4) // 4
        elif m == 4:
            if n in {5, 6, 9}:
                return n + 1
            else:
                return n
        elif m == 5:
            if n == 7:
                return (6 * n + 6) // 5
            else:
                return (6 * n + 8) // 5
        elif m == 6:
            if n % 7 == 1:
                return (10 * n + 10) // 7
            else:
                return (10 * n + 12) // 7
        else:
            # 处理m>6的情况，根据问题描述，这可能不会发生
            return 0
