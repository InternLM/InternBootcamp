from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cnamingcompany.Cnamingcompany_reward_calculator import CnamingcompanyRewardCalculator

# 导入依赖库
import random
import string
import re




class CnamingcompanyInteraction(BaseInteraction):
    """Cnamingcompany交互管理器"""
    
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
        score = CnamingcompanyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnamingcompany问题！"""
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
    @staticmethod
    def _calculate_answer(s, t):
        """与参考算法保持完全一致的实现"""
        first = sorted(s)
        second = sorted(t, reverse=True)
        n = len(first)
        ans = [''] * n

        split = n // 2
        f = first[:split]
        s_part = second[:split]

        if n % 2:
            f.append(first[split])

        l, r = 0, n-1
        fl, fr = 0, len(f)-1
        sl, sr = 0, len(s_part)-1

        for idx in range(n):
            if idx % 2 == 0:  # Oleg's turn
                if idx == n-1:
                    ans[l] = f[fl]
                    break
                if f[fl] >= s_part[sl]:
                    ans[r] = f[fr]
                    r -= 1
                    fr -= 1
                else:
                    ans[l] = f[fl]
                    l += 1
                    fl += 1
            else:  # Igor's turn
                if idx == n-1:
                    ans[l] = s_part[sl]
                    break
                if s_part[sl] <= f[fl]:
                    ans[r] = s_part[sr]
                    r -= 1
                    sr -= 1
                else:
                    ans[l] = s_part[sl]
                    l += 1
                    sl += 1
        return ''.join(ans)
