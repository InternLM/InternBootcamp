from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.character_puzzles.cfoxandnames.Cfoxandnames_reward_calculator import CfoxandnamesRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def solve_puzzle(names):
    graph = defaultdict(list)
    for c in string.ascii_lowercase:  # 初始化所有字母节点
        graph[c] = []
    
    # 构建字母约束关系图
    for i in range(len(names)-1):
        a, b = names[i], names[i+1]
        min_len = min(len(a), len(b))
        j = 0
        while j < min_len and a[j] == b[j]:
            j += 1
        
        if j == min_len:  # 处理前缀情况
            if len(a) > len(b):
                return "Impossible"
            continue
        
        # 添加字符顺序约束：a[j]必须出现在b[j]之前
        x, y = a[j], b[j]
        graph[y].append(x)  # 修正方向：y依赖x → x必须出现在y前面
    
    # 拓扑排序
    in_degree = {c:0 for c in string.ascii_lowercase}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1
    
    queue = deque([c for c in string.ascii_lowercase if in_degree[c] == 0])
    top_order = []
    
    while queue:
        u = queue.popleft()
        top_order.append(u)
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    return "Impossible" if len(top_order)!=26 else "".join(reversed(top_order))


class CfoxandnamesInteraction(BaseInteraction):
    """Cfoxandnames交互管理器"""
    
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
        score = CfoxandnamesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cfoxandnames问题！"""
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
    def _generate_names(self, n):
        names = set()
        char_pool = random.sample(string.ascii_lowercase, random.randint(3,5))  # 限制字符集增加冲突

        while len(names) < n:
            length = random.randint(self.min_length, self.max_length)
            name = "".join(random.choices(char_pool, k=length))
            names.add(name)
        return list(names)
