from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnamequest.Cnamequest_reward_calculator import CnamequestRewardCalculator

# 导入依赖库
import re
import random
import string




class CnamequestInteraction(BaseInteraction):
    """Cnamequest交互管理器"""
    
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
        score = CnamequestRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cnamequest问题！"""
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
    def _generate_valid_t(self, s):
        """生成有效t字符串（保证s是t的子序列且存在分割点）"""
        # 生成左右部分各包含s的构造
        left = []
        ptr = 0
        for c in s:
            # 在字符前添加随机前缀
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            left.append(c)
            ptr += 1
        left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))

        right = []
        ptr = 0
        for c in s:
            # 在字符后添加随机后缀
            right.append(c)
            right.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 3))))
            ptr += 1

        return (''.join(left) + ''.join(right)).replace('\x00', '')  # 防止空字符

    def _generate_invalid_t(self, s):
        """生成无效t字符串（保证至少有一半不满足条件）"""
        # 首先生成有效左半部分
        left = []
        ptr = 0
        for c in s:
            left.append(''.join(random.choices(string.ascii_lowercase, k=random.randint(0, 2))))
            left.append(c)
        left = ''.join(left)

        # 生成无效右半部分（不包含s）
        right = ''.join(random.choices(string.ascii_lowercase, 
                      k=random.randint(len(s)+1, len(s)*2)))
        while self._is_subsequence(s, right):
            right = ''.join(random.choices(string.ascii_lowercase, 
                          k=random.randint(len(s)+1, len(s)*2)))

        return left + right

    def _is_subsequence(self, s, t):
        """正确实现子序列判断"""
        it = iter(t)
        return all(c in it for c in s)

    def _adjust_length(self, t):
        """确保t长度在合理范围内"""
        t = t[:self.t_max_len]
        while len(t) < self.t_min_len:
            t += random.choice(string.ascii_lowercase)
        return t
