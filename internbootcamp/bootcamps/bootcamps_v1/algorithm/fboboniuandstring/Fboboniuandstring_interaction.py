from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fboboniuandstring.Fboboniuandstring_reward_calculator import FboboniuandstringRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def solve_bn_case(dots):
    n = len(dots)
    l = -1
    r = 10**7
    final_dot = (0, 0)
    while r - l > 1:
        mid = (l + r) // 2
        minx = -10**7
        maxx = 10**7
        miny = -10**7
        maxy = 10**7
        minXY = -10**7
        maxXY = 10**7
        
        for x, y in dots:
            minx = max(minx, x - mid)
            maxx = min(maxx, x + mid)
            miny = max(miny, y - mid)
            maxy = min(maxy, y + mid)
            minXY = max(minXY, (x - y) - mid)
            maxXY = min(maxXY, (x - y) + mid)
        
        may_be = (minx <= maxx) and (miny <= maxy) and (minXY <= maxXY)
        if may_be:
            lower_bound = minx - maxy
            upper_bound = maxx - miny
            if lower_bound > maxXY or upper_bound < minXY:
                may_be = False
        
        if may_be:
            x_t = minx
            y_t = maxy
            if (x_t - y_t) < minXY:
                move = min(maxx - x_t, minXY - (x_t - y_t))
                x_t += move
                if (x_t - y_t) < minXY:
                    move = min(y_t - miny, minXY - (x_t - y_t))
                    y_t -= move
            x_t = max(x_t, 0)
            y_t = max(y_t, 0)
            if x_t == 0 and y_t == 0:
                x_t = 1
                y_t = 0
            final_dot = (x_t, y_t)
            r = mid
        else:
            l = mid
    return r, final_dot


class FboboniuandstringInteraction(BaseInteraction):
    """Fboboniuandstring交互管理器"""
    
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
        score = FboboniuandstringRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Fboboniuandstring问题！"""
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

