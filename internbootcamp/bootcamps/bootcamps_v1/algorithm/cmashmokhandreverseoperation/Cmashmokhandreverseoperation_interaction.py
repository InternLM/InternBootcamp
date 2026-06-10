from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmashmokhandreverseoperation.Cmashmokhandreverseoperation_reward_calculator import CmashmokhandreverseoperationRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answers(n, a, queries):
    aa = a.copy()
    m = len(queries)
    res = []
    
    if n == 0:
        return [0] * m  # Only one element, no possible inversions
    
    if n < 2:
        a1, a2 = aa[0], aa[1]
        original_inversion = 1 if a1 > a2 else 0
        reversed_inversion = 1 if a2 > a1 else 0
        current_inversion = original_inversion
        f = False  # Tracks whether the array is reversed
        for q in queries:
            if q != 0:
                f = not f
                current_inversion = reversed_inversion if f else original_inversion
            res.append(current_inversion)
        return res
    
    n2 = 2 ** n
    acc0 = []
    acc1 = []
    
    # Initialize for q=1 and q=2 levels
    a00 = a01 = a10 = a11 = 0
    for i in range(0, n2, 4):
        a_val = aa[i]
        b_val = aa[i+1] if i+1 < n2 else 0
        c_val = aa[i+2] if i+2 < n2 else 0
        d_val = aa[i+3] if i+3 < n2 else 0
        
        a00 += (b_val < a_val) + (d_val < c_val)
        a01 += (c_val < a_val) + (c_val < b_val) + (d_val < a_val) + (d_val < b_val)
        a10 += (b_val > a_val) + (d_val > c_val)
        a11 += (c_val > a_val) + (c_val > b_val) + (d_val > a_val) + (d_val > b_val)
    
    acc0 = [a00, a01]
    acc1 = [a10, a11]
    w = 4
    
    while w < n2:
        a00 = 0
        a10 = 0
        for i in range(0, n2, w * 2):
            le = sorted(aa[i:i + w])
            ri = sorted(aa[i + w:i + w * 2])
            
            # Compute a00 (inversions from left to right)
            i_le, j_ri, cnt = 0, 0, 0
            while i_le < len(le) and j_ri < len(ri):
                if le[i_le] > ri[j_ri]:
                    j_ri += 1
                else:
                    cnt += j_ri
                    i_le += 1
            cnt += j_ri * (len(le) - i_le)
            a00 += cnt
            
            # Compute a10 (inversions from right to left)
            i_ri, j_le, cnt = 0, 0, 0
            while i_ri < len(ri) and j_le < len(le):
                if ri[i_ri] > le[j_le]:
                    j_le += 1
                else:
                    cnt += j_le
                    i_ri += 1
            cnt += j_le * (len(ri) - i_ri)
            a10 += cnt
        
        acc0.append(a00)
        acc1.append(a10)
        w *= 2
    
    # Handling queries by swapping acc0 and acc1 as needed
    for q in queries:
        current_q = q
        # Flip all levels up to q
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
        res.append(sum(acc0))
        # Restore original state for next query
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
                
    return res


class CmashmokhandreverseoperationInteraction(BaseInteraction):
    """Cmashmokhandreverseoperation交互管理器"""
    
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
        score = CmashmokhandreverseoperationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmashmokhandreverseoperation问题！"""
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

