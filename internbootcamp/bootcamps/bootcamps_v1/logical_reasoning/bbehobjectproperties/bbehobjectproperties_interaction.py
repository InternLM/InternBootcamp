from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bbehobjectproperties.bbehobjectproperties_reward_calculator import BbehobjectpropertiesRewardCalculator

# 导入依赖库
import json
import random
import re
from copy import deepcopy




class BbehobjectpropertiesInteraction(BaseInteraction):
    """Bbehobjectproperties交互管理器"""
    
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
        score = BbehobjectpropertiesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个bbehobjectproperties问题！"""
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
