import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class BsimplexmlInstructionGenerator(BaseInstructionGenerator):
    """Bsimplexml Bootcamp指令生成器"""
    
    def __init__(self, max_depth=3, max_children=2):
        """
        初始化Bsimplexml指令生成器
        
        Args:
            max_depth: 参数描述
            max_children: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'max_depth': max_depth,
            'max_children': max_children  # 控制每个节点最大子节点数
        }
    
    def case_generator(self):
        def build_xml(current_depth):
            # 保证至少生成一个根标签
            if current_depth > self.params['max_depth']:
                return ''
            
            tag = random.choice('abcdefghijklmnopqrstuvwxyz')
            xml = [f'<{tag}>']
            
            # 随机决定是否生成子节点
            if current_depth < self.params['max_depth'] and random.random() < 0.8:
                num_children = random.randint(1, self.params['max_children'])
                for _ in range(num_children):
                    xml.append(build_xml(current_depth + 1))
            
            xml.append(f'</{tag}>')
            return ''.join(xml)
        
        # 确保根标签有效
        xml_str = build_xml(0)
        return {'xml': xml_str}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        xml_input = question_case['xml']
        return f"""请严格按照以下规则格式化给定的Bsimplexml文本：

格式规范：
1. 每个标签（包括开标签和闭标签）必须独占一行
2. 行首缩进使用2个空格乘以当前嵌套层级：
   - 根标签层级为0（无缩进）
   - 子标签层级逐层递增
   - 闭标签与对应开标签保持相同层级
3. 标签格式保持原始大小写（均为小写字母）

输入示例：
输入：<a><b><c></c></b><d></d></a>
正确输出：
<a>
  <b>
    <c>
    </c>
  </b>
  <d>
  </d>
</a>

需要处理的Bsimplexml：
{xml_input}

请将最终结果包裹在[answer]标签内。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

