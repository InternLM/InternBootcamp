from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cmushroomstrife.Cmushroomstrife_reward_calculator import CmushroomstrifeRewardCalculator

# 导入依赖库
import math
import random
from functools import reduce
from collections import deque

# === 源文件中的全局函数 ===

def lcm(a, b):
    return a * b // math.gcd(a, b)

def solve_case(n, m, edges):
    try:
        # 预处理阶段增加输入合法性校验
        for u, v, g, l in edges:
            if g > l or l % g != 0:
                return (False, None)
            if math.gcd(g, l//g) != 1:
                return (False, None)

        a0 = [1] * n
        # 构建a0阶段
        for u, v, g, _ in edges:
            a0[u-1] = lcm(a0[u-1], g)
            a0[v-1] = lcm(a0[v-1], g)

        # 构建关系图
        adjacency = [[] for _ in range(n)]
        for u, v, g, l in edges:
            u_idx, v_idx = u-1, v-1
            k_base = lcm(a0[u_idx], a0[v_idx])
            if l % k_base != 0:
                return (False, None)
            k = l // k_base
            adjacency[u_idx].append((v_idx, k, g))
            adjacency[v_idx].append((u_idx, k, g))

        # 连通分量处理
        solution = [1] * n
        visited = [False] * n
        for i in range(n):
            if visited[i]:
                continue
                
            # BFS遍历连通分量
            q = deque([i])
            visited[i] = True
            divisors = []
            for node in q:
                for _, k, _ in adjacency[node]:
                    divisors.append(k)
            
            # 计算最大公约数
            base_divisor = reduce(math.gcd, divisors, 0) if divisors else 1
            
            # 寻找有效因子
            found = False
            for d in range(1, base_divisor + 1):
                if base_divisor % d != 0:
                    continue
                    
                temp_sol = {i: d}
                valid = True
                bfs_q = deque([i])
                
                while bfs_q and valid:
                    current = bfs_q.popleft()
                    current_d = temp_sol[current]
                    
                    for neighbor, k, g in adjacency[current]:
                        required = k // current_d
                        
                        if neighbor in temp_sol:
                            if temp_sol[neighbor] != required:
                                valid = False
                                break
                            continue
                            
                        if k % current_d != 0:
                            valid = False
                            break
                            
                        # 验证边条件
                        a_val = a0[current] * current_d
                        b_val = a0[neighbor] * required
                        if math.gcd(a_val, b_val) != g or lcm(a_val, b_val) != (a_val * b_val) // g:
                            valid = False
                            break
                            
                        temp_sol[neighbor] = required
                        bfs_q.append(neighbor)
                        
                if valid:
                    for node in temp_sol:
                        solution[node] = temp_sol[node]
                    found = True
                    break
                    
            if not found:
                return (False, None)

        # 最终有效性检查
        final = [a0[i] * solution[i] for i in range(n)]
        for num in final:
            if not (1 <= num <= 10**6):
                return (False, None)
                
        for u, v, g, l in edges:
            a, b = final[u-1], final[v-1]
            if math.gcd(a, b) != g or lcm(a, b) != l:
                return (False, None)
                
        return (True, final)
        
    except:
        return (False, None)


class CmushroomstrifeInteraction(BaseInteraction):
    """Cmushroomstrife交互管理器"""
    
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
        score = CmushroomstrifeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmushroomstrife问题！"""
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
    def _generate_valid_case(self):
        """生成保证有解的案例"""
        while True:
            n = random.randint(self.min_n, self.max_n)
            max_edges = n*(n-1)//2
            m = random.randint(self.min_m, min(self.max_m, max_edges))

            # 生成合法顶点值
            nodes = [random.randint(1, 100) for _ in range(n)]  # 小范围便于生成合法边
            edges = []

            # 随机选择不重复的边
            existing_edges = set()
            for _ in range(m):
                while True:
                    u = random.randint(1, n)
                    v = random.randint(1, n)
                    if u != v and (u, v) not in existing_edges and (v, u) not in existing_edges:
                        break
                existing_edges.add((u, v))

                a, b = nodes[u-1], nodes[v-1]
                g = math.gcd(a, b)
                l = lcm(a, b)
                edges.append((u, v, g, l))

            case = {"n": n, "m": m, "edges": edges}
            # 验证生成的案例确实有解
            possible, _ = solve_case(n, m, edges)
            if possible:
                return case

    def _generate_invalid_case(self):
        """生成保证无解的案例"""
        while True:
            n = random.randint(max(2, self.min_n), self.max_n)  # 至少2个节点才能有边
            m = random.randint(1, min(self.max_m, n*(n-1)//2))

            edges = []
            existing_edges = set()

            # 强制至少包含一个矛盾边
            invalid_added = False
            for _ in range(m):
                u = random.randint(1, n)
                v = random.randint(1, n)
                while u == v or (u, v) in existing_edges or (v, u) in existing_edges:
                    u = random.randint(1, n)
                    v = random.randint(1, n)

                existing_edges.add((u, v))

                if not invalid_added and random.random() < 0.5:
                    # 生成矛盾的gcd和lcm对
                    g = random.randint(2, 50)
                    l = g * random.randint(1, 100) + random.randint(1, g-1)  # 保证l % g != 0
                    invalid_added = True
                else:
                    # 生成合法对
                    a = random.randint(1, 100)
                    b = random.randint(1, 100)
                    g = math.gcd(a, b)
                    l = lcm(a, b)

                edges.append((u, v, g, l))

            case = {"n": n, "m": m, "edges": edges}
            possible, _ = solve_case(n, m, edges)
            if not possible:
                return case
