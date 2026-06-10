from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bonlinemeeting.Bonlinemeeting_reward_calculator import BonlinemeetingRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class BonlinemeetingInteraction(BaseInteraction):
    """Bonlinemeeting交互管理器"""
    
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
        score = BonlinemeetingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bonlinemeeting问题！"""
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
    def solve_leader(n, messages):
        m = len(messages)
        a = [0]*(m+1)  # 操作数组（1-based）
        b = [0]*(m+1)  # 用户数组（1-based）

        # 解析操作
        for i in range(1, m+1):
            op, id_str = messages[i-1].split()
            a[i] = 1 if op == '+' else -1
            b[i] = int(id_str)

        # 第一遍处理：初始化s数组
        l = defaultdict(int)  # 记录用户最后一次操作位置
        s = [0]*(m+2)  # 前缀和数组

        for i in range(1, m+1):
            user = b[i]
            # 处理首次登出但之前未登录的情况
            if a[i] == -1 and l[user] == 0:
                s[0] += 1  # 初始未在线但收到登出
            s[i] = a[i]
            l[user] = i

        # 计算在线人数前缀和
        for i in range(1, m+1):
            s[i] += s[i-1]

        # 转换为在线状态标记（1在线，0离线）
        for i in range(m+1):
            s[i] = 1 if s[i] > 0 else 0

        # 转换为累计在线时间
        for i in range(1, m+1):
            s[i] += s[i-1]

        # 第二遍处理：验证候选者
        l = defaultdict(int)  # 重置记录
        v = [0]*(n+1)  # 违规标记

        for i in range(1, m+1):
            user = b[i]
            if a[i] == 1:  # 登录事件
                violation = False
                if l[user] == 0:  # 首次登录
                    if s[i-1] > 0:  # 登录前已有在线
                        violation = True
                else:  # 非首次登录
                    prev = l[user]
                    if (s[i-1] - s[prev-1]) > 0:  # 两次登录之间有其他人
                        violation = True

                if violation:
                    v[user] = 1
            l[user] = i  # 更新最后操作位置

        # 检查最后一次登出后的状态
        for user in range(1, n+1):
            last_op_idx = l[user]
            if last_op_idx != 0 and a[last_op_idx] == -1:  # 最后操作是登出
                if (s[m] - s[last_op_idx-1]) > 0:  # 登出后仍有其他人
                    v[user] = 1

        # 收集未违规的候选人
        leaders = [user for user in range(1, n+1) if v[user] == 0]
        return sorted(leaders)
