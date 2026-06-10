import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import re
import random

# === 源文件中的全局函数 ===

def compute_expected_outputs(n, m, edges, queries):
    vert = defaultdict(list)
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    
    # 修正边处理逻辑：u为较大编号的员工（初始薪金更高）
    for a, b in edges:
        u = max(a, b)
        v = min(a, b)
        vert[u].append(v)
        indeg[u] += 1
        outdeg[v] += 1
    
    ans = 0
    for i in range(1, n+1):
        ans += indeg[i] * outdeg[i]
    expected = [ans]
    
    for v in queries:
        # 移除当前节点贡献
        ans -= indeg[v] * outdeg[v]
        
        # 处理所有指向v的边（反向边）
        sons = list(vert[v])
        for son in sons:
            # 移除son节点原有贡献
            ans -= indeg[son]
            # 增加反转边后的贡献
            ans += (outdeg[son] - 1)
            
            # 调整度数
            indeg[v] -= 1
            outdeg[v] += 1
            indeg[son] += 1
            outdeg[son] -= 1
            
            # 添加反向边
            vert[son].append(v)
        
        # 清空原边
        vert[v].clear()
        # 添加新贡献
        ans += indeg[v] * outdeg[v]
        expected.append(ans)
    
    return expected


class FkonradandcompanyevaluationInstructionGenerator(BaseInstructionGenerator):
    """Fkonradandcompanyevaluation Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, max_q=5):
        """
        初始化Fkonradandcompanyevaluation指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_q = max_q
    
    def case_generator(self):
        # 确保至少1名员工
        n = random.randint(1, self.max_n)
        
        # 生成有效敌意对
        possible_pairs = []
        if n >= 2:
            for i in range(1, n+1):
                for j in range(i+1, n+1):
                    possible_pairs.append( (j, i) )  # 保证u > v
            random.shuffle(possible_pairs)
        
        m = min(self.max_m, len(possible_pairs))
        m = random.randint(0, m) if possible_pairs else 0
        edges = possible_pairs[:m]
        
        # 生成有效查询序列
        q = random.randint(0, self.max_q)
        queries = [random.randint(1, n) for _ in range(q)]
        
        # 计算期望输出
        expected = compute_expected_outputs(n, m, edges, queries)
        
        # 确保计算结果有效
        while len(expected) != q + 1:
            return self.case_generator()  # 重新生成
        
        return {
            'n': n,
            'm': m,
            'edges': edges,
            'queries': queries,
            'expected_outputs': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        prompt = [
            "As Konrad, compute dangerous triples after each salary update.",
            f"Employees: {case['n']}, Dislike pairs: {case['m']}"
        ]
        if case['m'] > 0:
            prompt.append("Dislike relationships:")
            prompt.extend(f"{b} {a}" for a, b in case['edges'])  # 显示为原始输入顺序
        else:
            prompt.append("No dislike relationships.")
        
        prompt.append(f"Salary updates ({len(case['queries'])} days):")
        prompt.extend(map(str, case['queries']))
        
        prompt.append(
            "Output q+1 integers. Place answer list in [answer][/answer]."
            "\nExample: [answer][0,1,2][/answer]"
        )
        return "\n".join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

