from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cbarcode.Cbarcode_reward_calculator import CbarcodeRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_min_pixels(n, m, x, y, rows):
    # 转置行以获取各列
    cols = list(zip(*rows))
    u = [col.count('.') for col in cols]  # 每列改为白色所需的修改次数（即列中黑色像素数）
    v = [n - count for count in u]        # 每列改为黑色所需的修改次数（即列中白色像素数）
    
    a = [u[0]]  # 以白色结尾的段的最小修改次数
    b = [v[0]]  # 以黑色结尾的段的最小修改次数
    s = x - 1   # 段长度至少为x，因此需要保留前s个状态
    
    # 处理前x-1列
    for i in range(1, x):
        # 由于段长度必须>=x，此时只能继续延长当前颜色段
        a = [float('inf')] + [prev + u[i] for prev in a]
        b = [float('inf')] + [prev + v[i] for prev in b]
    
    # 处理x到min(y, m)-1列
    for i in range(x, min(y, m)):
        # 可以开始新的颜色段，此时需要取另一种颜色的最小值
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a]
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b]
        a, b = new_a, new_b
    
    # 处理剩下的列（当m > y时）
    for i in range(min(y, m), m):
        # 需要确保段长度不超过y，因此保留前y个状态
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a[:-1]]  # 保留前y-1个状态
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b[:-1]]
        a, b = new_a, new_b
    
    # 最后，取所有可能状态中的最小值
    valid_a = a[s:] if a[s:] else [float('inf')]
    valid_b = b[s:] if b[s:] else [float('inf')]
    return min(min(valid_a), min(valid_b))


class CbarcodeInteraction(BaseInteraction):
    """Cbarcode交互管理器"""
    
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
        score = CbarcodeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cbarcode问题！"""
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

