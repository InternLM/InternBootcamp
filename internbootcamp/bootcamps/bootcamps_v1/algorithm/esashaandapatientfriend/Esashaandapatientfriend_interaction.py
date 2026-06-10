from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esashaandapatientfriend.Esashaandapatientfriend_reward_calculator import EsashaandapatientfriendRewardCalculator

# 导入依赖库
import random
import re
import bisect
from bisect import bisect_left
from bisect import bisect_right




class EsashaandapatientfriendInteraction(BaseInteraction):
    """Esashaandapatientfriend交互管理器"""
    
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
        score = EsashaandapatientfriendRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Esashaandapatientfriend问题！"""
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
    def _gen_lr(self, event_times):
        """生成合理的l和r范围"""
        if event_times:
            min_t = event_times[0]
            max_t = event_times[-1]
            l = random.randint(max(1, min_t-10), max_t+10)
            r = random.randint(l, min(self.max_time, max_t+1000))
        else:
            l = random.randint(1, 100)
            r = random.randint(l, min(self.max_time, l+1000))
        return l, r

    @staticmethod
    def _simulate(events, l, r, v_initial):
        if v_initial == 0:
            return l  # 初始值为0立即破裂

        current_time = l
        current_speed = 0  # 初始速度
        v = v_initial
        sorted_events = sorted(events, key=lambda x: x["t"])

        for event in sorted_events:
            t_event = event["t"]
            s_new = event["s"]

            # 处理当前时间段 [current_time, t_event)
            if t_event > current_time:
                dt = t_event - current_time
                if current_speed < 0:
                    # 计算在当前速度下是否会耗尽
                    if v <= 0:
                        return current_time
                    time_to_empty = v / (-current_speed)
                    if time_to_empty <= dt:
                        return current_time + time_to_empty
                    # 不会耗尽，更新v和时间
                    v += current_speed * dt
                    current_time = t_event
                else:
                    v += current_speed * dt
                    current_time = t_event
                if v <= 0:
                    return current_time  # 刚好在时间点耗尽

            # 更新速度
            current_speed = s_new

        # 处理最后的时间段 [current_time, r)
        dt = r - current_time
        if dt > 0:
            if current_speed < 0:
                if v <= 0:
                    return current_time
                time_to_empty = v / (-current_speed)
                if time_to_empty <= dt:
                    return current_time + time_to_empty
                v += current_speed * dt
            else:
                v += current_speed * dt
            if v <= 0:
                return r  # 在结束时间点耗尽

        return -1 if v > 0 else r
