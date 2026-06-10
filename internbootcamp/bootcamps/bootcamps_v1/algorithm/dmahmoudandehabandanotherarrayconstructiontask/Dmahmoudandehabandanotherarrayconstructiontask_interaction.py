from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dmahmoudandehabandanotherarrayconstructiontask.Dmahmoudandehabandanotherarrayconstructiontask_reward_calculator import DmahmoudandehabandanotherarrayconstructiontaskRewardCalculator

# 导入依赖库
import random




class DmahmoudandehabandanotherarrayconstructiontaskInteraction(BaseInteraction):
    """Dmahmoudandehabandanotherarrayconstructiontask交互管理器"""
    
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
        score = DmahmoudandehabandanotherarrayconstructiontaskRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dmahmoudandehabandanotherarrayconstructiontask问题！"""
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
    def generate_b(a):
        MAX_NUM = 2000000
        prime_str = ('2 3 5 7 11 13 17 19 23 29 '
                     '31 37 41 43 47 53 59 61 67 71 '
                     '73 79 83 89 97 101 103 107 109 113 '
                     '127 131 137 139 149 151 157 163 167 173 '
                     '179 181 191 193 197 199 211 223 227 229 '
                     '233 239 241 251 257 263 269 271 277 281 '
                     '283 293 307 311 313 317')
        prime_list = [int(p) for p in prime_str.split()]
        used = [False] * (MAX_NUM + 1)
        n = len(a)
        b = []

        def record(x):
            t = []
            tmp_x = x
            for p in prime_list:
                if tmp_x % p == 0:
                    while tmp_x % p == 0:
                        tmp_x = tmp_x // p
                    t.append(p)
                    if tmp_x == 1:
                        break
            if tmp_x != 1:
                t.append(tmp_x)
            for ti in t:
                if ti > MAX_NUM:
                    continue
                for i in range(ti, MAX_NUM + 1, ti):
                    used[i] = True

        for ai in a:
            if ai <= MAX_NUM and not used[ai]:
                b.append(ai)
                record(ai)
            else:
                temp = ai + 1
                while temp <= MAX_NUM and used[temp]:
                    temp += 1
                if temp > MAX_NUM:
                    temp = ai + 1
                b.append(temp)
                record(temp)
                break  # Break after first replacement

        temp = 2
        while len(b) < len(a):
            while temp <= MAX_NUM and used[temp]:
                temp += 1
            if temp > MAX_NUM:
                break
            b.append(temp)
            record(temp)
            temp += 1

        return b
