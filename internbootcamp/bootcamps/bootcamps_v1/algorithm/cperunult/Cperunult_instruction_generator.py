import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CperunultInstructionGenerator(BaseInstructionGenerator):
    """Cperunult Bootcamp指令生成器"""
    
    def __init__(self, n=3, m=2, b=1000, inc=10, d=50, max_time_events=100, force_infinite=False):
        """
        初始化Cperunult指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            b: 参数描述
            inc: 参数描述
            d: 参数描述
            max_time_events: 参数描述
            force_infinite: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        assert n >= 1 and m >= 0
        assert b >= 1 and inc >= 0 and d >= 1
        self.n = n
        self.m = m
        self.b = b
        self.inc = inc
        self.d = d
        self.max_time_events = max_time_events
        self.force_infinite = force_infinite  # 强制生成无限解案例
    
    def case_generator(self):
        while True:
            enemies = []
            valid_case = False
            infinite_possible = self.force_infinite

            # 生成基础参数
            base_inc = self.inc
            base_d = self.d

            # 强制无限解模式
            if infinite_possible:
                base_inc = random.randint(1, 100)
                base_d = random.randint(100, 1000)
                for _ in range(self.n):
                    mh = random.randint(1, base_d)  # 确保最大生命<=d
                    sh = random.randint(0, mh)
                    reg = 0 if random.random() < 0.5 else random.randint(0, 5)
                    enemies.append({'h': mh, 'sh': sh, 'r': reg})
                break

            # 正常模式生成
            for _ in range(self.n):
                # 确保存在有效解法
                mh = random.randint(base_d//2, base_d*2)
                sh = random.randint(0, mh)
                reg = random.randint(0, 10)
                
                # 控制必杀场景
                if random.random() < 0.3:
                    sh = random.randint(0, base_d)
                
                enemies.append({'h': mh, 'sh': sh, 'r': reg})
                if sh <= base_d or (reg > 0 and mh > base_d):
                    valid_case = True

            if valid_case or self.m > 0:
                break

        # 生成事件
        events = []
        event_dict = defaultdict(dict)
        for _ in range(self.m):
            e = random.randint(1, self.n)
            for _ in range(10):  # 尝试生成有效事件
                t = random.randint(0, self.max_time_events)
                if t not in event_dict[e]:
                    enemy = enemies[e-1]
                    h_val = random.randint(0, enemy['h'])
                    
                    # 确保事件有意义
                    if enemy['r'] == 0 and random.random() < 0.7:
                        h_val = random.randint(0, base_d)
                    elif enemy['r'] > 0:
                        h_val = random.randint(max(0, base_d - 50), min(enemy['h'], base_d + 50))
                    
                    event_dict[e][t] = h_val
                    events.append({'t': t, 'e': e, 'h': h_val})
                    break

        # 按敌兵分组后排序时间
        grouped_events = defaultdict(list)
        for event in events:
            grouped_events[event['e']].append(event)
        
        sorted_events = []
        for e in sorted(grouped_events.keys()):
            sorted_events.extend(sorted(grouped_events[e], key=lambda x: x['t']))

        return {
            'n': self.n,
            'm': self.m,
            'b': self.b,
            'inc': self.inc,
            'd': self.d,
            'enemies': enemies,
            'events': sorted_events
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = [
            "Vlad需要选择最优时间发动技能'Cperunult'来最大化金币收益。",
            f"参数说明：",
            f"- 敌人数量：{question_case['n']}，事件数：{question_case['m']}",
            f"- 基础赏金：B={question_case['b']}, 时间加成：INC={question_case['inc']}/秒，技能伤害：D={question_case['d']}",
            "\n敌人属性（最大生命值, 初始生命值, 生命恢复/秒）："
        ]
        
        for idx, enemy in enumerate(question_case['enemies'], 1):
            prompt.append(f"敌兵{idx}: {enemy['h']} {enemy['sh']} {enemy['r']}")
        
        if question_case['m'] > 0:
            prompt.append("\n生命值更新事件（时间, 敌兵编号, 新生命值）：")
            for event in question_case['events']:
                prompt.append(f"在 {event['t']} 秒时，敌兵 {event['e']} 的生命值变更为 {event['h']}")

        prompt.extend([
            "\n请计算Vlad能获得的最大金币数（若为无穷大输出-1），",
            "将最终答案用[answer]标签包裹，例如：[answer]3000[/answer]或[answer]-1[/answer]"
        ])
        
        return '\n'.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

