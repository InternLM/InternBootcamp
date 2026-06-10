from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.btheworldisjustaprogrammingtaskhardversion.Btheworldisjustaprogrammingtaskhardversion_reward_calculator import BtheworldisjustaprogrammingtaskhardversionRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_balance_and_count(s):
    balance = 0
    min_balance = 0
    count = 0
    prefix = []
    for c in s:
        balance += 1 if c == '(' else -1
        prefix.append(balance)
        if balance < min_balance:
            min_balance = balance
            count = 1
        elif balance == min_balance:
            count += 1
    return min_balance, count, prefix

def calculate_real_beauty(s):
    total = sum(1 if c == '(' else -1 for c in s)
    if total != 0:
        return 0
    min_balance, count, prefix = compute_min_balance_and_count(s)
    overall_min = min(prefix)
    if overall_min < 0:
        return 0
    return count

def optimal_solution(n, s):
    max_beauty = 0
    best_pair = (1, 1)
    original_beauty = calculate_real_beauty(s)
    max_beauty = original_beauty
    
    s_list = list(s)
    for i in range(n):
        for j in range(i, n):
            if s_list[i] == s_list[j]:
                continue
            
            # Perform swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
            new_s = ''.join(s_list)
            current_beauty = calculate_real_beauty(new_s)
            
            if current_beauty > max_beauty:
                max_beauty = current_beauty
                best_pair = (i+1, j+1)
            
            # Revert swap
            s_list[i], s_list[j] = s_list[j], s_list[i]
    
    return (max_beauty, best_pair[0], best_pair[1])


class BtheworldisjustaprogrammingtaskhardversionInteraction(BaseInteraction):
    """Btheworldisjustaprogrammingtaskhardversion交互管理器"""
    
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
        score = BtheworldisjustaprogrammingtaskhardversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Btheworldisjustaprogrammingtaskhardversion问题！"""
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

