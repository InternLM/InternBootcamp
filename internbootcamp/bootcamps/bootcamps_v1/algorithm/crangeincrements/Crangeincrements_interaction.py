from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.crangeincrements.Crangeincrements_reward_calculator import CrangeincrementsRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def solve(a_list):
    n = len(a_list)
    l = a_list.copy()
    ans = []
    s = []
    opened = []
    for i in range(n):
        current = l[i]
        if not s or current > s[-1]:
            s.append(current)
            opened.append(i + 1)
        elif current < s[-1]:
            while s and current < s[-1]:
                pp = True
                base = current
                if len(s) > 1:
                    base = max(base, s[-2])
                if base == current:
                    pp = False
                val = s[-1] - base
                while val > 0:
                    ans.append(f"{opened[-1]} {i}")
                    val -= 1
                if pp:
                    s.pop()
                    opened.pop()
                else:
                    break
            if s:
                s[-1] = current
    while s:
        base = 0
        if len(s) > 1:
            base = s[-2]
        val = s[-1] - base
        while val > 0:
            ans.append(f"{opened[-1]} {n}")
            val -= 1
        s.pop()
        opened.pop()
    operations = []
    for op in ans:
        li, ri = map(int, op.split())
        operations.append((li, ri))
    return operations


class CrangeincrementsInteraction(BaseInteraction):
    """Crangeincrements交互管理器"""
    
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
        score = CrangeincrementsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Crangeincrements问题！"""
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

