from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cperunult.Cperunult_reward_calculator import CperunultRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from io import StringIO
import sys

# === 源文件中的全局函数 ===

def solve(input_str):
    # 保持原解题逻辑不变，确保正确性
    from collections import defaultdict

    sys.stdin = StringIO(input_str)
    old_stdout = sys.stdout
    sys.stdout = output = StringIO()

    try:
        n, m = map(int, sys.stdin.readline().split())
        b, inc, d = map(int, sys.stdin.readline().split())
        dat = list(map(int, sys.stdin.read().split()))
        j = n * 3
        ev = [[] for _ in range(n)]
        a = defaultdict(int)
        for _ in range(m):
            t = dat[j]
            i = dat[j+1]
            h = dat[j+2]
            ev[i-1].append((t, h))
            j += 3
        j = 0
        c = 0
        infinite_flag = False
        for i in range(n):
            mh = dat[j]
            sh = dat[j+1]
            reg = dat[j+2]
            ev[i].sort()
            h = sh
            p = 0
            on = (h <= d)
            if on:
                c += 1
            if reg > 0:
                if mh <= d and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    if on:
                        if (d - h) < 0:
                            x = p + ((d - h) // reg) + 1
                        else:
                            x = p + (d - h) // reg + 1
                        if x < t:
                            a[x] -= 1
                            on = False
                    non = (nh <= d)
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
                    h = nh
                if on:
                    x = p + (d - h) // reg + 1
                    a[x] -= 1
            else:
                if on and inc > 0:
                    infinite_flag = True
                    break
                for (t, nh) in ev[i]:
                    non = nh <= d
                    if on != non:
                        a[t] += 1 if non else -1
                    on = non
                    p = t
            j += 3
        if infinite_flag:
            print(-1)
        else:
            ans = c * b
            sorted_times = sorted(a.keys())
            for t in sorted_times:
                y = c * (b + (t - 1) * inc)
                if ans < y:
                    ans = y
                c += a[t]
            print(ans)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sys.stdout = old_stdout
    return output.getvalue().strip()


class CperunultInteraction(BaseInteraction):
    """Cperunult交互管理器"""
    
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
        score = CperunultRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cperunult问题！"""
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

