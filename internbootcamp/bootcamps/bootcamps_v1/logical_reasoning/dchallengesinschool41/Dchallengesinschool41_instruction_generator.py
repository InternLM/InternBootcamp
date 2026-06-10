import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Dchallengesinschool41InstructionGenerator(BaseInstructionGenerator):
    """Dchallengesinschool41 Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dchallengesinschool41指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.params.setdefault('max_n', 10)
        self.params.setdefault('min_n', 2)
        self.params.setdefault('max_k', 1000)
    
    def case_generator(self):
        def generate_valid_initial(n):
            # 确保生成至少一个RL对的初始配置
            for _ in range(10):
                s = [random.choice(['L', 'R']) for _ in range(n)]
                if any(s[i] == 'R' and s[i+1] == 'L' for i in range(n-1)):
                    return ''.join(s)
                # 强制插入一个RL对
                pos = random.randint(0, n-2) if n >=2 else 0
                s[pos] = 'R'
                s[pos+1] = 'L'
                return ''.join(s)
            return 'RL' + 'L'*(n-2) if n >=2 else 'RL'

        n = random.randint(self.params['min_n'], self.params['max_n'])
        # 50%概率生成有效案例
        if random.random() < 0.5:
            # 生成有效案例
            s = generate_valid_initial(n)
            mini, maxi, _ = self.compute_min_max(s)
            if maxi == 0:
                return {'n':4, 'k':2, 'initial':'RLRL'}  # 保底案例
            k = random.randint(mini, maxi)
            return {'n':n, 'k':k, 'initial':s}
        else:
            # 生成无效案例
            s = ''.join(random.choice(['L', 'R']) for _ in range(n))
            mini, maxi, _ = self.compute_min_max(s)
            # 生成无效的k值
            if maxi == 0:
                k = random.randint(1, self.params['max_k'])  # 无解情况
            else:
                k = random.choice([
                    random.randint(0, mini-1),
                    random.randint(maxi+1, self.params['max_k'])
                ])
            return {'n':n, 'k':k, 'initial':s}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        initial = question_case['initial']
        return f"""## 谜题挑战：学生转头协调

{n}个学生排成一列，初始朝向：{initial}  
（L=向左看，R=向右看）

**游戏规则**：
1. 每秒钟可以同时翻转多个相邻的RL对（左边学生向右看，右边向左看）
2. 每次翻转后，这对学生会变成LL和RR
3. 必须恰好经过{k}秒完成所有操作
4. 最终不能有任何相邻的RL对存在

**输出格式要求**：
- 共{k}行，每行表示每秒的操作
- 每行格式：首个数字表示翻转对数n_i，后面跟着n_i个**左学生的位置编号**（1-based）
- 位置编号必须按升序排列且不重复
- 同一秒的操作位置不能相邻

将最终答案放在[answer]和[/answer]之间，例如：
[answer]
2 1 3
1 2
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_max(s):
        s_list = list(s)
        steps = []
        while True:
            pairs = []
            i = 0
            while i < len(s_list)-1:
                if s_list[i] == 'R' and s_list[i+1] == 'L':
                    pairs.append(i+1)  # 1-based左位置
                    s_list[i] = 'L'
                    s_list[i+1] = 'R'
                    i += 2
                else:
                    i += 1
            if not pairs:
                break
            steps.append(pairs)
        return len(steps), sum(len(step) for step in steps), steps
