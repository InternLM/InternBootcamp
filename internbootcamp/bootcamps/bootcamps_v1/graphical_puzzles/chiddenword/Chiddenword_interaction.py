from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.chiddenword.Chiddenword_reward_calculator import ChiddenwordRewardCalculator

# 导入依赖库
import re
import string
import random




class ChiddenwordInteraction(BaseInteraction):
    """Chiddenword交互管理器"""
    
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
        score = ChiddenwordRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chiddenword问题！"""
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
    def generate_solution(s_input):
        s = s_input
        st = 0
        en = 0
        ans = [['.' for _ in range(13)] for _ in range(2)]
        found = False
        for i in range(ord('A'), ord('Z') + 1):
            c = chr(i)
            st = s.find(c)
            if st == -1:
                continue
            en = s.find(c, st + 1)
            if en != -1:
                found = True
                break
        if not found:
            return "Impossible"

        if st + 1 == en:
            return "Impossible"
        else:
            l = (en - st)
            l += l % 2
            ss = 13 - (l // 2)
            p = [ss, 0]
            dr = 1
            for i in range(st, en):
                ans[p[1]][p[0]] = s[i]
                if p[0] + dr == 13:
                    p[1] += 1
                    dr *= -1
                else:
                    p[0] += dr
            p = [ss - 1, 0]
            dr = -1
            a = s[:st]
            b = s[en + 1:]
            bf = a[::-1] + b[::-1]
            for i in range(len(bf)):
                if p[0] < 0:
                    p[0] = 0
                    p[1] = 1
                    dr = 1
                ans[p[1]][p[0]] = bf[i]
                p[0] += dr
            row0 = ''.join(ans[0])
            row1 = ''.join(ans[1])
            return [row0, row1]
