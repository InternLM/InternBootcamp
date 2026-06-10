import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re
from copy import deepcopy




class BbehobjectpropertiesInstructionGenerator(BaseInstructionGenerator):
    """Bbehobjectproperties Bootcamp指令生成器"""
    
    def __init__(self, min_items=3 ,max_items=50, max_steps=5):
        """
        初始化Bbehobjectproperties指令生成器
        
        Args:
            min_items: 参数描述
            max_items: 参数描述
            max_steps: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化谜题训练场，配置生成参数

        参数:
            max_items: 初始物品数量上限（默认50）
            max_steps: 操作步骤数量（默认5）
        """
        self.min_items = min_items
        self.max_items = max_items
        self.max_steps = max_steps

        # 定义可能属性值域
        self.sizes = ["extra-extra-small", "extra-small", "small", "medium", 
                     "large", "extra-large", "extra-extra-large"]
        self.origins = ['Spanish', 'Turkish', 'French', 'Russian', 'British',
                       'Mexican', 'Afghan', 'Portuguese', 'Canadian', 'Japanese',
                       'Iranian', 'Italian', 'German', 'Chinese', 'Polish', 'Brazilian']
        self.materials = ["plastic", "steel", "glass", "ceramic", "concrete"]
        self.smells = ['vinegar', 'pine needles', 'freshly cut grass', 'coffee',
                      'rose', 'citrus fruits', 'lavender', 'burning wood', 'garlic',
                      'gasoline', 'coconut', 'popcorn', 'wet dog', 'leather',
                      'baking bread', 'chocolate', 'vanilla']
        self.names = ['calculator', 'hat', 'jar', 'plier', 'sunglasses', 'drill',
                     'canvas', 'ring', 'screwdriver', 'camera', 'bird', 'ruler',
                     'hammer', 'umbrella', 'shoe', 'cup', 'fork', 'key', 'house',
                     'brush', 'book', 'candle', 'bicycle', 'vase', 'clock', 'sofa',
                     'trash can', 'marker', 'bottle', 'banana']
    
    def case_generator(self):
        # 生成初始物品集合
        case = self._generate_initial_case()
        # 应用多层修改步骤
        case = self._apply_operations(case)
        # 生成最终问题条件
        case["question"] = self._generate_question(case["final_objects"])
        # 计算正确答案
        case["correct_answer"] = self._compute_correct_answer(case["final_objects"], case["question"])
        return case
    
    @staticmethod
    def prompt_func(case):
        # 构建问题提示文本
        prompt = ["I had a collection of {} weird items that went through a few changes. Initially:".format(len(case["initial_objects"]))]
        
        # 添加初始物品描述
        for i, obj in enumerate(case["initial_objects"], 1):
            prompt.append("{}. a {} {} {} made of {} with a smell of {}.".format(
                i, obj['size'], obj['origin'], obj['name'], obj['material'], obj['smell']))
        
        # 添加颜色分布描述
        color_desc = ["The color of the items was respectively as follows:"]
        count = 0
        for block in case["color_blocks"]:
            count += block["count"]
            color_desc.append("the {} {} were {}".format(
                "next" if count > block["count"] else "first",
                block["count"],
                block["color"]
            ))
        prompt.append(" ".join(color_desc).replace(" 1 were", " 1 was") + ".")
        
        # 添加操作步骤描述
        for step in case["steps"]:
            prompt.append(step["description"])
        
        # 添加最终问题
        conditions = []
        for attr, cond in case["question"].items():
            if cond["type"] == "negated":
                conditions.append("{} is not {}".format(attr, cond["value"]))
            elif cond["type"] == "or":
                conditions.append("either " + " or ".join(cond["values"]))
        prompt.append("In my current collection, how many items have the following attributes: {}? "
                      "If the exact number cannot be computed, the answer must be 'unknown'.\n"
                      "Please put your final answer within [answer][/answer] tags.".format(", ".join(conditions)))
        
        return "\n".join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_initial_case(self):
        # 生成颜色分布
        n = random.randint(self.min_items, self.max_items)
        colors = ["beige", "blue", "crimson", "cyan", "gold", "gray", "green",
                 "indigo", "khaki", "magenta", "maroon", "orange", "pink", 
                 "purple", "teal", "violet", "white", "yellow"]

        color_blocks = []
        remaining = n
        while remaining > 0:
            color = random.choice(colors)
            count = random.randint(1, min(5, remaining))
            color_blocks.append({"color": color, "count": count})
            remaining -= count

        # 生成物品对象
        objects = []
        color_idx = 0
        current_count = 0
        for _ in range(n):
            if current_count >= color_blocks[color_idx]["count"]:
                color_idx += 1
                current_count = 0

            obj = {
                "size": random.choice(self.sizes),
                "origin": random.choice(self.origins),
                "material": random.choice(self.materials),
                "smell": random.choice(self.smells),
                "name": random.choice(self.names),
                "color": color_blocks[color_idx]["color"]
            }
            objects.append(obj)
            current_count += 1

        return {
            "initial_objects": objects,
            "color_blocks": color_blocks,
            "steps": [],
            "final_objects": deepcopy(objects),
            "correct_answer": None
        }

    def _apply_operations(self, case):
        # 生成随机操作步骤
        for _ in range(self.max_steps):
            case = self._apply_random_operation(case)
        return case

    def _apply_random_operation(self, case):
        # 随机选择一个操作类型并应用
        operation_type = random.choice(["add_copies", "replace_size", "modify_material"])

        if operation_type == "add_copies":
            return self._add_color_copies(case)
        elif operation_type == "replace_size":
            return self._replace_size(case)
        else:
            return self._modify_material(case)

    def _add_color_copies(self, case):
        # 添加指定颜色的副本
        target_color = random.choice(list({b["color"] for b in case["color_blocks"]}))
        new_color = random.choice([c for c in self.smells if c != target_color])

        new_objects = []
        for obj in case["final_objects"]:
            new_objects.append(obj)
            if obj["color"] == target_color:
                new_obj = deepcopy(obj)
                new_obj.update({
                    "color": new_color,
                    "origin": random.choice(self.origins),
                    "size": random.choice(self.sizes)
                })
                new_objects.append(new_obj)

        case["final_objects"] = new_objects

        description_tplts = []
        description_tplts.append("Then, my relative added copies of all {} items, changing their color to {}.")
        description_tplts.append("Then, copies of all {} items were added, changing their color to {}.")
        description_tplts.append("Next, all {} items were duplicated, altering their color to {}.")
        description_tplts.append("After that, copies of all {} items were created, modifying their color to {}.")
        description_tplts.append("Subsequently, all {} items were replicated, transforming their color to {}.")
        description_tplts.append("Following this, copies of all {} items were made, shifting their color to {}.")
        description_tplts.append("Then, all {} items were copied, updating their color to {}.")
        description_tplts.append("Next, the color of all {} items was changed to {} by creating copies.")
        description_tplts.append("After that, the color of all {} items was updated to {} through duplication.")
        description_tplts.append("Subsequently, all {} items were cloned, with their color adjusted to {}.")
        description_tplts.append("Following this, the color of all {} items was modified to {} by making copies.") 
        case["steps"].append({
            "type": "add_copies",
            "description": random.choice(description_tplts).format(
                target_color, new_color)
        })
        return case

    def _replace_size(self, case):
        # 替换某些对象的尺寸
        final_objects = case["final_objects"]

        # 确保至少有一个对象的尺寸被替换
        existing_sizes = {obj["size"] for obj in final_objects}
        if not existing_sizes:
            raise ValueError("No objects found to replace size.")

        # 随机选择一个目标尺寸
        target_size = random.choice(list(existing_sizes))

        # 确保新尺寸与目标尺寸不同
        available_sizes = [s for s in self.sizes if s != target_size]
        if not available_sizes:
            raise ValueError("No available sizes to replace with.")
        new_size = random.choice(available_sizes)

        # 更新对象尺寸
        updated_objects = []
        replaced = False  # 标记是否进行了替换
        for obj in final_objects:
            if obj["size"] == target_size:
                new_obj = deepcopy(obj)
                new_obj["size"] = new_size
                updated_objects.append(new_obj)
                replaced = True
            else:
                updated_objects.append(obj)

        # 如果没有替换任何对象，抛出异常
        if not replaced:
            raise ValueError(f"No objects found with size '{target_size}' to replace.")

        # 更新案例数据
        case["final_objects"] = updated_objects
        case["steps"].append({
            "type": "replace_size",
            "description": "Then, I replaced all {} items with {} ones.".format(target_size, new_size)
        })
        return case

    def _modify_material(self, case):
        # 修改某些对象的材质
        existing_materials = [obj["material"] for obj in case["final_objects"]]
        target_material = random.choice(existing_materials)
        new_material = random.choice([m for m in self.materials if m != target_material])

        updated_objects = []
        for obj in case["final_objects"]:
            if obj["material"] == target_material:
                new_obj = deepcopy(obj)
                new_obj["material"] = new_material
                updated_objects.append(new_obj)
            else:
                updated_objects.append(obj)

        case["final_objects"] = updated_objects
        case["steps"].append({
            "type": "modify_material",
            "description": "Then, I changed all {} items to be made of {}.".format(target_material, new_material)
        })
        return case

    def _generate_question(self, objects):
        # 生成随机问题条件
        attrs = ["color", "size", "material", "smell", "origin"]
        selected = random.sample(attrs, random.randint(2,len(attrs)))

        question_type = random.choice(["negated", "or"])
        conditions = {}
        for attr in selected:
            values = list(set(obj[attr] for obj in objects))
            target = random.choice(values)
            if question_type == "negated":
                conditions[attr] = {
                    "type": question_type,
                    "value": target
                }
            elif question_type == "or":
                conditions[attr] = {
                    "type": question_type,
                    "values": random.sample(values, random.randint(1, len(values)))
                }
        return conditions

    def _compute_correct_answer(self, objects, question):
        """
        根据问题条件计算正确答案
        """
        def matches_condition(obj, condition):
            attr, cond = condition
            if cond["type"] == "negated":
                return obj[attr] != cond["value"]
            elif cond["type"] == "or":
                return obj[attr] in cond["values"]
            return False

        # 筛选符合条件的对象
        valid_objects = []
        for obj in objects:
            if all(matches_condition(obj, (attr, cond)) for attr, cond in question.items()):
                valid_objects.append(obj)

        # 返回符合条件的对象数量
        return len(valid_objects)
