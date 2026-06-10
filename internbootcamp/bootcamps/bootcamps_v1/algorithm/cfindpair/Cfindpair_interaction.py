from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cfindpair.Cfindpair_reward_calculator import CfindpairRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_kth_pair(n, k, array):
    vs = sorted(array)  # 确保排序逻辑正确
    p = k - 1
    lenvs = len(vs)
    
    # 处理极端情况
    if lenvs == 0: return (None, None)
    if lenvs == 1: return (vs[0], vs[0])
    
    # 主计算逻辑
    prow = p // lenvs
    vrow = vs[prow]
    
    # 寻找连续元素块边界
    prow0 = prow
    while prow0 > 0 and vs[prow0-1] == vrow:
        prow0 -= 1
    prow1 = prow + 1
    while prow1 < lenvs and vs[prow1] == vrow:
        prow1 += 1
    
    # 计算有效块尺寸
    block_size = prow1 - prow0
    block_start_index = prow0 * lenvs
    
    # 剩余位置计算
    remaining = p - block_start_index
    if remaining < 0:
        return (vs[p//lenvs], vs[p%lenvs])
    
    # 计算列位置
    col = remaining // block_size
    return (vrow, vs[col])


class CfindpairInteraction(BaseInteraction):
    """Cfindpair交互管理器"""
    
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
        score = CfindpairRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cfindpair问题！"""
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

