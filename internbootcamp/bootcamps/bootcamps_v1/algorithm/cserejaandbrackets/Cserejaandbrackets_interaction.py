from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cserejaandbrackets.Cserejaandbrackets_reward_calculator import CserejaandbracketsRewardCalculator

# 导入依赖库
import random
import re
import math




class CserejaandbracketsInteraction(BaseInteraction):
    """Cserejaandbrackets交互管理器"""
    
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
        score = CserejaandbracketsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cserejaandbrackets问题！"""
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
    def find_valid_regions(self, s):
        # 寻找有效括号子序列区域
        stack = []
        valid = []
        max_len = 0
        start = 0
        for i, c in enumerate(s):
            if c == '(':
                stack.append(i)
            else:
                if stack:
                    stack.pop()
                    if not stack:
                        valid.append((start, i))
                    else:
                        valid.append((stack[-1]+1, i))
                else:
                    start = i + 1
        return valid if valid else [(0, len(s)-1)]

    @staticmethod
    def compute_answers(s, queries):
        n = len(s)
        a = [0]*(n+1)
        for i in range(1, n+1):
            a[i] = a[i-1] + (1 if s[i-1] == '(' else -1)

        # 构建Sparse Table
        log_table = [0]*(n+2)
        for i in range(2, n+2):
            log_table[i] = log_table[i//2] + 1

        k_max = log_table[n] + 1 if n > 0 else 0
        st = [[0]*(n+1) for _ in range(k_max)]
        st[0] = a.copy()

        for k in range(1, k_max):
            for i in range(n+1 - (1 << k) + 1):
                st[k][i] = min(st[k-1][i], st[k-1][i + (1 << (k-1))])

        answers = []
        for li, ri in queries:
            l = li - 1
            r = ri
            length = r - l + 1
            k = log_table[length]
            mid = r - (1 << k) + 1

            min_val = min(st[k][l], st[k][mid])
            ans = (ri - li + 1) - (a[l] - min_val) - (a[r] - min_val)
            answers.append(max(ans // 1, 0))  # 确保结果为整数

        return answers
