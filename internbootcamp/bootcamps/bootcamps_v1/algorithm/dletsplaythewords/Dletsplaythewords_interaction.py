from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dletsplaythewords.Dletsplaythewords_reward_calculator import DletsplaythewordsRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_case(words):
    count = [0] * 4  # 00, 01, 10, 11
    swap = [[] for _ in range(4)]
    items = set(words)
    
    for i, s in enumerate(words):
        a = s[0]
        b = s[-1]
        pos = int(a) * 2 + int(b)
        count[pos] += 1
        reversed_s = s[::-1]
        if reversed_s not in items:
            swap[pos].append(i + 1)  # Using 1-based index
    
    if count[1] > count[2]:
        count[1], count[2] = count[2], count[1]
        swap[1], swap[2] = swap[2], swap[1]
    
    if count[1] + count[2] == 0:
        if count[0] > 0 and count[3] > 0:
            return (-1, None)
        else:
            return (0, [])
    else:
        diff = 0
        original_count_01 = count[1]
        original_count_10 = count[2]
        while count[2] - count[1] > 1:
            diff += 1
            count[2] -= 1
            count[1] += 1
        i = 1 if len(swap[1]) > len(swap[2]) else 2
        if len(swap[i]) >= diff:
            indexes = swap[i][:diff]
            return (diff, indexes)
        else:
            return (-1, None)


class DletsplaythewordsInteraction(BaseInteraction):
    """Dletsplaythewords交互管理器"""
    
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
        score = DletsplaythewordsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dletsplaythewords问题！"""
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

