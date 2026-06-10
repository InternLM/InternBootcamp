from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bthreereligions.Bthreereligions_reward_calculator import BthreereligionsRewardCalculator

# 导入依赖库
import random
import re
from typing import List
from typing import Dict
from typing import Any




class BthreereligionsInteraction(BaseInteraction):
    """Bthreereligions交互管理器"""
    
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
        score = BthreereligionsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bthreereligions问题！"""
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
    def get_expected_outputs(word: str, operations: List[str]) -> List[str]:
        n = len(word)
        nxt = [[n+1]*(n+2) for _ in range(26)]
        for i in range(n-1, -1, -1):
            c = ord(word[i]) - ord('a')
            nxt[c][i] = i
        for c in range(26):
            for j in range(n-1, -1, -1):
                if nxt[c][j] == n+1:
                    nxt[c][j] = nxt[c][j+1]
        dp = [[[n+1 for _ in range(251)] for __ in range(251)] for ___ in range(251)]
        dp[0][0][0] = 0
        l = [0, 0, 0]
        t = ['', '', '']
        expected_outputs = []
        for op in operations:
            parts = op.split()
            if parts[0] == '+':
                religion = int(parts[1]) - 1
                c = parts[2]
                t[religion] += c
                l[religion] += 1
                lim = [0, 0, 0]
                lim[religion] = l[religion]
                for i in range(lim[0], l[0]+1):
                    for j in range(lim[1], l[1]+1):
                        for k in range(lim[2], l[2]+1):
                            if i + j + k == 0:
                                continue
                            current_min = n+1
                            if i > 0:
                                pos = dp[i-1][j][k]
                                if pos <= n:
                                    char = t[0][i-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            if j > 0:
                                pos = dp[i][j-1][k]
                                if pos <= n:
                                    char = t[1][j-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            if k > 0:
                                pos = dp[i][j][k-1]
                                if pos <= n:
                                    char = t[2][k-1]
                                    new_pos = nxt[ord(char) - ord('a')][pos]
                                    if new_pos < n+1:
                                        current_min = min(current_min, new_pos + 1)
                            dp[i][j][k] = current_min
            else:
                religion = int(parts[1]) - 1
                t[religion] = t[religion][:-1]
                l[religion] -= 1
            current_dp = dp[l[0]][l[1]][l[2]]
            expected_outputs.append("YES" if current_dp <= n else "NO")
        return expected_outputs
