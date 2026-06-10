import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class BonlinemeetingInstructionGenerator(BaseInstructionGenerator):
    """Bonlinemeeting Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bonlinemeeting指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'n_min': params.get('n_min', 2),
            'n_max': params.get('n_max', 10),
            'm_min': params.get('m_min', 3),
            'm_max': params.get('m_max', 20),
        }
    
    def case_generator(self):
        n = random.randint(self.params['n_min'], self.params['n_max'])
        m = random.randint(self.params['m_min'], self.params['m_max'])
        
        messages = []
        user_states = defaultdict(bool)  # False表示离线
        
        for _ in range(m):
            user_id = random.randint(1, n)
            current_state = user_states[user_id]
            
            # 自动生成合法操作
            op = '-' if current_state else '+'
            messages.append(f"{op} {user_id}")
            user_states[user_id] = not current_state
        
        # 确保最后所有用户都离线
        for user in list(user_states.keys()):
            if user_states[user]:
                messages.append(f"- {user}")
                user_states[user] = False
        
        expected = self.solve_leader(n, messages)
        return {
            'n': n,
            'm': len(messages),  # 更新实际消息数
            'messages': messages,
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        messages = question_case['messages']
        
        prompt = (
            "你是F公司的助理董事，需要根据会议记录确定可能的团队领导者。领导者的定义是：在任何时刻，只要至少有一人在线，领导者必须在线。\n\n"
            "输入格式：\n"
            f"第一行包含两个整数n和m（{n} {m}），表示团队成员数和消息数。\n"
            "接下来m行每行格式为'+ id'或'- id'，表示用户id的登录/登出记录。\n\n"
            "输出要求：\n"
            "第一行为可能的领导者数量k，第二行为按升序排列的k个ID。若无可能领导者，仅输出0。\n\n"
            "当前会议记录：\n" +
            '\n'.join(messages) + "\n\n"
            "请将最终答案放置在[answer]和[/answer]标记之间，示例如下：\n"
            "[answer]\n"
            "2\n"
            "3 5\n"
            "[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
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
