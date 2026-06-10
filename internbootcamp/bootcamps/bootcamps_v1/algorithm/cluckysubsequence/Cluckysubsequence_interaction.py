from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cluckysubsequence.Cluckysubsequence_reward_calculator import CluckysubsequenceRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def calculate_answer(n, k, a):
    rest = 0
    lk = {}

    def islucky(x):
        nonlocal rest
        s = str(x)
        for c in s:
            if c not in {'4', '7'}:
                rest += 1
                return False
        lk[x] = lk.get(x, 0) + 1
        return True

    for elem in a:
        islucky(elem)

    llk = list(lk.values())
    m = len(llk)
    dp = {}

    def solve(ind, need):
        if need == 0:
            return 1
        if ind < 0 or need < 0 or ind + 1 < need:
            return 0
        if (ind, need) in dp:
            return dp[(ind, need)]
        res = (solve(ind-1, need) + solve(ind-1, need-1) * llk[ind]) % MOD
        dp[(ind, need)] = res
        return res

    facts = [1] * (n + 5)
    for i in range(2, len(facts)):
        facts[i] = (facts[i-1] * i) % MOD

    def comber(a_num, b_num):
        if b_num == 0:
            return 1
        if b_num > a_num or a_num < 0 or b_num < 0:
            return 0
        numerator = facts[a_num]
        denominator = (facts[b_num] * facts[a_num - b_num]) % MOD
        return (numerator * pow(denominator, MOD-2, MOD)) % MOD

    ans = 0
    max_i = min(m, k)
    for i in range(0, max_i + 1):
        needed = k - i
        if needed < 0 or needed > rest:
            continue
        way_lucky = solve(m-1, i) if m > 0 else (0 if i > 0 else 1)
        way_non_lucky = comber(rest, needed)
        ans = (ans + way_lucky * way_non_lucky) % MOD
    return ans


class CluckysubsequenceInteraction(BaseInteraction):
    """Cluckysubsequence交互管理器"""
    
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
        score = CluckysubsequenceRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cluckysubsequence问题！"""
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
    def is_lucky(x):
        s = str(x)
        return all(c in {'4', '7'} for c in s)

    def generate_lucky_number(self):
        return int(''.join(random.choice(['4', '7']) for _ in range(random.randint(1, 4))))

    def generate_non_lucky_number(self):
        while True:
            num = random.randint(1, 10**9)
            s = list(str(num))
            if any(c not in {'4', '7'} for c in s):
                return num
            # 强制修改最后一位为非幸运数字
            s[-1] = random.choice(['0', '1', '2', '3', '5', '6', '8', '9'])
            return int(''.join(s))
