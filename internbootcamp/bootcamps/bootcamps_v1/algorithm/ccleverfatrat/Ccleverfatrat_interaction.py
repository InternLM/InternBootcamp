from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccleverfatrat.Ccleverfatrat_reward_calculator import CcleverfatratRewardCalculator

# 导入依赖库
import re
import random
from functools import reduce

# === 源文件中的全局变量 ===

max_oats = 10**6 + 1



# === 源文件中的全局函数 ===

def create_goals(ws):
    wrapped_ws = []
    for row in ws:
        new_row = [max_oats] + row + [max_oats]
        wrapped_ws.append(new_row)
    goal_oats = []
    pre_goal_oat = [0, 0]
    for idx in range(len(wrapped_ws)-1, -1, -1):
        goal_oat = []
        for jdx in range(1, len(wrapped_ws[idx])-1):
            current_ws = wrapped_ws[idx][jdx]
            left_parent = pre_goal_oat[jdx-1]
            right_parent = pre_goal_oat[jdx]
            goal_value = max(current_ws, min(left_parent, right_parent))
            goal_oat.append(goal_value)
        goal_oats.append(goal_oat)
        pre_goal_oat = [max_oats] + goal_oat + [max_oats]
    goal_oats.reverse()
    return goal_oats

def possible_oats(oats_list, current_ws):
    new_oats = []
    for idx in range(len(current_ws)):
        current_threshold = current_ws[idx]
        available_mass = sum([m for (m, _) in oats_list[idx]])
        if available_mass >= current_threshold:
            left = oats_list[idx-1] if idx > 0 else None
            right = oats_list[idx] if idx < len(oats_list)-1 else None
            new_mass = available_mass
            if left is not None:
                new_left = left + [(new_mass, (idx-1, idx))]
                new_oats.append(new_left)
            if right is not None:
                new_right = right + [(new_mass, (idx, idx+1))]
                new_oats.append(new_right)
    return new_oats

def is_break_all(goal_layer, oats_list):
    for idx, threshold in enumerate(goal_layer):
        if idx >= len(oats_list):
            continue
        total_mass = sum([m for (m, _) in oats_list[idx]])
        if total_mass >= threshold:
            return True
    return False

def fatrat(state):
    try:
        a, ws = state['a'], state['ws']
        goals = create_goals(ws)
        current_layer = [[(m, (0, i))] for i, m in enumerate(a)]
        
        for level in range(len(ws)):
            current_goal = goals[level]
            if is_break_all(current_goal, current_layer):
                return "Cerealguy"
            if level == len(ws)-1:
                break
            current_layer = possible_oats(current_layer, ws[level])
            if not current_layer:
                break
        
        final_check = any(len(grp) > 0 for grp in current_layer)
        return "Cerealguy" if final_check else "Fat Rat"
    except:
        return "Fat Rat"


class CcleverfatratInteraction(BaseInteraction):
    """Ccleverfatrat交互管理器"""
    
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
        score = CcleverfatratRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccleverfatrat问题！"""
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

