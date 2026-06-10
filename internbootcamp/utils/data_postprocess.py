"""
数据后处理工具

支持对 evaluator 输出的 jsonl 文件进行灵活的过滤和转换处理
- 可插拔的 filter 函数
- 可插拔的转换函数（支持一对一或一对多）
"""

import json
import hashlib
import jsonlines
import base64
import io
from typing import Callable, List, Dict, Any, Optional, Union
from pathlib import Path
from collections import defaultdict
from PIL import Image


class DataPostProcessor:
    """
    数据后处理器
    
    功能:
    1. 读取 evaluator 输出的 jsonl 文件
    2. 应用过滤函数筛选数据
    3. 应用转换函数转换数据（支持一对一或一对多）
    4. 输出新的 jsonl 文件
    
    示例用法:
        # 创建处理器
        processor = DataPostProcessor()
        
        # 注册过滤函数
        processor.add_filter(lambda x: x.get("success") == True)
        processor.add_filter(lambda x: x.get("score", 0) > 0.5)
        
        # 注册转换函数
        processor.add_transformer(extract_training_data)
        
        # 执行处理
        processor.process(
            input_path="eval_results.jsonl",
            output_path="filtered_results.jsonl"
        )
    """
    
    def __init__(self):
        """初始化数据处理器"""
        self.filters: List[Callable[[Dict[str, Any]], bool]] = []
        self.transformers: List[Callable[[Dict[str, Any]], Union[Dict[str, Any], List[Dict[str, Any]]]]] = []
        self.stats = defaultdict(int)
    
    def add_filter(self, filter_func: Callable[[Dict[str, Any]], bool], name: Optional[str] = None):
        """
        添加过滤函数
        
        Args:
            filter_func: 过滤函数，接收一个字典，返回布尔值
                        返回 True 表示保留该数据，False 表示过滤掉
            name: 过滤函数的名称（可选，用于统计）
        
        示例:
            processor.add_filter(lambda x: x.get("success") == True)
            processor.add_filter(lambda x: x.get("score", 0) > 0.5, name="high_score")
        """
        if name:
            filter_func._filter_name = name
        self.filters.append(filter_func)
        return self
    
    def add_transformer(self, transform_func: Callable[[Dict[str, Any]], Union[Dict[str, Any], List[Dict[str, Any]]]], name: Optional[str] = None):
        """
        添加转换函数
        
        Args:
            transform_func: 转换函数，接收一个字典，返回一个字典或字典列表
                           - 返回字典表示一对一转换
                           - 返回列表表示一对多转换
                           - 返回 None 表示跳过该数据
            name: 转换函数的名称（可选，用于统计）
        
        示例:
            # 一对一转换
            processor.add_transformer(lambda x: {"text": x["messages"][-1]["content"]})
            
            # 一对多转换
            def split_by_turns(data):
                return [{"turn": i, "msg": msg} for i, msg in enumerate(data["messages"])]
            processor.add_transformer(split_by_turns)
        """
        if name:
            transform_func._transform_name = name
        self.transformers.append(transform_func)
        return self
    
    def clear_filters(self):
        """清空所有过滤函数"""
        self.filters.clear()
        return self
    
    def clear_transformers(self):
        """清空所有转换函数"""
        self.transformers.clear()
        return self
    
    def _apply_filters(self, data: Dict[str, Any]) -> bool:
        """
        应用所有过滤函数
        
        Args:
            data: 待过滤的数据
        
        Returns:
            bool: True 表示通过所有过滤器，False 表示被过滤
        """
        for filter_func in self.filters:
            try:
                if not filter_func(data):
                    filter_name = getattr(filter_func, '_filter_name', 'unnamed')
                    self.stats[f'filtered_by_{filter_name}'] += 1
                    return False
            except Exception as e:
                print(f"⚠️ 过滤函数执行出错: {e}")
                self.stats['filter_errors'] += 1
                return False
        return True
    
    def _apply_transformers(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        应用所有转换函数
        
        Args:
            data: 待转换的数据
        
        Returns:
            List[Dict[str, Any]]: 转换后的数据列表（可能为空）
        """
        results = [data]
        
        for transform_func in self.transformers:
            new_results = []
            for item in results:
                try:
                    transformed = transform_func(item)
                    
                    # 处理不同的返回类型
                    if transformed is None:
                        # 跳过该数据
                        continue
                    elif isinstance(transformed, list):
                        # 一对多转换
                        new_results.extend(transformed)
                        self.stats['one_to_many_transforms'] += len(transformed) - 1
                    elif isinstance(transformed, dict):
                        # 一对一转换
                        new_results.append(transformed)
                    else:
                        print(f"⚠️ 转换函数返回了不支持的类型: {type(transformed)}")
                        self.stats['transform_type_errors'] += 1
                        
                except Exception as e:
                    print(f"⚠️ 转换函数执行出错: {e}")
                    self.stats['transform_errors'] += 1
            
            results = new_results
        
        return results
    
    def process(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        verbose: bool = True
    ) -> Dict[str, int]:
        """
        处理 jsonl 文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）。如果不提供，将自动生成为 input_path_processed.jsonl
            verbose: 是否打印详细信息
        
        Returns:
            Dict[str, int]: 处理统计信息
        """
        input_path = Path(input_path)
        
        # 如果未提供输出路径，自动生成
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_processed{input_path.suffix}"
        else:
            output_path = Path(output_path)
        
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 重置统计信息
        self.stats = defaultdict(int)
        
        if verbose:
            print(f"📖 正在读取输入文件: {input_path}")
        
        # 处理数据
        with jsonlines.open(input_path) as reader, \
             jsonlines.open(output_path, mode='w') as writer:
            
            for line in reader:
                self.stats['total_input'] += 1
                
                # 应用过滤器
                if not self._apply_filters(line):
                    self.stats['total_filtered'] += 1
                    continue
                
                # 应用转换器
                transformed_items = self._apply_transformers(line)
                
                # 写入结果
                for item in transformed_items:
                    writer.write(item)
                    self.stats['total_output'] += 1
        
        if verbose:
            self._print_stats()
            print(f"✅ 处理完成，结果已保存到: {output_path}")
        
        return dict(self.stats)
    
    def _print_stats(self):
        """打印统计信息"""
        print(f"\n{'='*60}")
        print(f"📊 数据处理统计")
        print(f"{'='*60}")
        print(f"输入数据总数: {self.stats['total_input']}")
        print(f"过滤掉的数据: {self.stats['total_filtered']}")
        print(f"输出数据总数: {self.stats['total_output']}")
        
        if self.stats['one_to_many_transforms'] > 0:
            print(f"一对多转换新增: {self.stats['one_to_many_transforms']}")
        
        if self.stats['filter_errors'] > 0:
            print(f"⚠️ 过滤错误数: {self.stats['filter_errors']}")
        
        if self.stats['transform_errors'] > 0:
            print(f"⚠️ 转换错误数: {self.stats['transform_errors']}")
        
        if self.stats['transform_type_errors'] > 0:
            print(f"⚠️ 转换类型错误数: {self.stats['transform_type_errors']}")
        
        # 打印各个过滤器的统计
        filter_stats = {k: v for k, v in self.stats.items() if k.startswith('filtered_by_')}
        if filter_stats:
            print(f"\n按过滤器分类统计:")
            for filter_name, count in filter_stats.items():
                print(f"  - {filter_name}: {count}")
        
        print(f"{'='*60}\n")


# ============= 预定义的常用过滤函数 =============

def filter_by_success(data: Dict[str, Any]) -> bool:
    """只保留成功的样本"""
    return data.get("success", False) == True


def filter_by_score(min_score: float = 0.0, max_score: float = 1.0) -> Callable:
    """
    按分数范围过滤
    
    Args:
        min_score: 最小分数（包含）
        max_score: 最大分数（包含）
    
    Returns:
        过滤函数
    """
    def _filter(data: Dict[str, Any]) -> bool:
        score = data.get("score", 0)
        return min_score <= score <= max_score
    return _filter


def filter_by_data_source(data_source: str) -> Callable:
    """
    按数据源过滤
    
    Args:
        data_source: 数据源名称
    
    Returns:
        过滤函数
    """
    def _filter(data: Dict[str, Any]) -> bool:
        return data.get("input", {}).get("data_source") == data_source
    return _filter


def filter_by_field(field_path: str, expected_value: Any, default: Any = None) -> Callable:
    """
    按字段值过滤（支持嵌套字段）
    
    Args:
        field_path: 字段路径，用点号分隔，例如 "input.extra_info.generator_name"
        expected_value: 期望的值
        default: 字段不存在时的默认值
    
    Returns:
        过滤函数
    
    示例:
        filter_by_field("input.extra_info.split", "test")
        filter_by_field("score", 1.0)
    """
    def _filter(data: Dict[str, Any]) -> bool:
        # 解析嵌套字段
        value = data
        for key in field_path.split('.'):
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return False
        return value == expected_value
    return _filter


def filter_by_design_end(data: Dict[str, Any]) -> bool:
    """
    检查 messages 字段中最后一条消息是否包含 <Design End>
    如果不包含则过滤掉
    
    Args:
        data: 数据字典
    
    Returns:
        bool: True 表示最后一条消息包含 <Design End>，False 表示不包含（将被过滤）
    """
    messages = data.get("messages", [])
    if not messages:
        return False
    
    # 获取最后一条消息
    last_message = messages[-1]
    if not isinstance(last_message, dict):
        return False
    
    # 检查 content 字段是否包含 <Design End>
    content = last_message.get("content", "")
    if not isinstance(content, str):
        return False
    
    return "<Design End>" in content


# ============= 预定义的常用转换函数 =============

def expand_messages_prefixes(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """将多轮对话按assistant消息展开为前缀集"""
    result_data: List[Dict[str, Any]] = []
    full_message = data.get("messages", [])
    prompt_message = []
    input_data = data.get("input", {})
    if "prompt" in input_data and input_data["prompt"] is not None:
        prompt_message = input_data["prompt"]
    elif "messages" in input_data and input_data["messages"] is not None:
        prompt_message = input_data["messages"]
    else:
        raise ValueError("prompt or messages is not found in input")
    
    # 找到full_message中所有assistant角色的消息索引
    prompt_len = len(prompt_message)
    assistant_indices = []
    for i in range(prompt_len, len(full_message)):
        if isinstance(full_message[i], dict) and full_message[i].get("role") == "assistant":
            assistant_indices.append(i)
    
    # 按每个assistant消息拆分：prompt + 第一条asst, prompt + 第一条asst + 中间消息 + 第二条asst, ...
    for idx in assistant_indices:
        prefix = full_message[:idx+1]  # 从开始到当前assistant消息（包含）
        temp_data = data.copy()
        temp_data["messages"] = prefix
        result_data.append(temp_data)
    
    return result_data

def extract_messages_only(data: Dict[str, Any]) -> Dict[str, Any]:
    """提取对话消息"""
    return {
        "messages": data.get("messages", []),
        "score": data.get("score", 0),
        "success": data.get("success", False)
    }


def extract_for_training(data: Dict[str, Any]) -> Dict[str, Any]:
    """提取用于训练的数据"""
    new_data = {
        "data_source": data.get("input", {}).get("data_source"),
        "prompt": data.get("input", {}).get("prompt", []),
        "messages": data.get("messages", []),
        "tools": data.get("tools", []),
    }
    new_data = generate_id_to_data(new_data)
    return new_data


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_image_path(image_url: str) -> Optional[Path]:
    """将图片路径解析为可读取的本地路径。"""
    if not image_url or image_url.startswith("data:image"):
        return None

    image_path = Path(image_url)
    if image_path.is_absolute() and image_path.exists():
        return image_path

    candidate_paths = [
        Path.cwd() / image_path,
        _REPO_ROOT / image_path,
    ]
    for candidate in candidate_paths:
        if candidate.exists():
            return candidate
    return None


def get_image_wh(image_url: str) -> Optional[List[int]]:
    """获取图片宽高，返回 [width, height]。"""
    try:
        if image_url.startswith("data:image"):
            encoded = image_url.split(",", 1)[1] if "," in image_url else ""
            if not encoded:
                return None
            with Image.open(io.BytesIO(base64.b64decode(encoded))) as img:
                return [img.width, img.height]

        image_path = _resolve_image_path(image_url)
        if image_path is None:
            return None

        with Image.open(image_path) as img:
            return [img.width, img.height]
    except Exception:
        return None


def _has_multimodal_content(messages: List[Dict[str, Any]]) -> bool:
    """检查消息中是否包含 image_url。"""
    for message in messages:
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for item in content:
            if isinstance(item, dict) and item.get("type") == "image_url":
                return True
    return False


def _normalize_multimodal_content(content: Any) -> Any:
    """
    规范化多模态 content:
    1. 为 image_url 补充 image_wh
    2. 将 <image> 占位符统一为 <IMG_CONTEXT>
    3. 若文本中缺失占位符，则按图片数量补齐
    4. 输出格式统一为: [image_url..., text]
    """
    if not isinstance(content, list):
        return content

    image_items: List[Dict[str, Any]] = []
    text_parts: List[str] = []

    for item in content:
        if not isinstance(item, dict):
            continue

        item_type = item.get("type")
        if item_type == "image_url" and isinstance(item.get("image_url"), dict):
            normalized_item = {
                "type": "image_url",
                "image_url": dict(item["image_url"]),
            }
            image_url = normalized_item["image_url"].get("url", "")
            image_wh = get_image_wh(image_url)
            if image_wh is not None:
                normalized_item["image_url"]["image_wh"] = image_wh
            image_items.append(normalized_item)
        elif item_type == "text":
            text = item.get("text", "")
            if isinstance(text, str):
                text_parts.append(text.replace("<image>", "<IMG_CONTEXT>"))

    if not image_items:
        return content

    merged_text = "".join(text_parts).strip()
    placeholder_count = merged_text.count("<IMG_CONTEXT>")
    missing_placeholders = max(0, len(image_items) - placeholder_count)
    if missing_placeholders:
        prefix = "\n".join(["<IMG_CONTEXT>"] * missing_placeholders)
        merged_text = f"{prefix}\n{merged_text}" if merged_text else prefix

    return image_items + [{"type": "text", "text": merged_text}]


def normalize_messages_for_multimodal_sft(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """仅在检测到 image_url 时，对 messages 做多模态 SFT 格式规范化。"""
    if not _has_multimodal_content(messages):
        return messages

    normalized_messages: List[Dict[str, Any]] = []
    for message in messages:
        normalized_message = dict(message)
        normalized_message["content"] = _normalize_multimodal_content(message.get("content"))
        normalized_messages.append(normalized_message)
    return normalized_messages


def _simplify_messages_for_sft(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将 evaluator 风格的 messages 压缩成更接近 OpenAI chat-completions SFT 的格式:
    1. 保留 system/user/assistant/tool
    2. 保留 role/content/tool_calls/tool_call_id
    3. 丢弃 refusal/annotations/reasoning_content/audio 等非训练核心字段
    4. assistant 若是 tool call 消息，则保留 tool_calls
    """
    simplified_messages: List[Dict[str, Any]] = []

    for message in messages:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        if role not in {"system", "user", "assistant", "tool"}:
            continue

        simplified_message: Dict[str, Any] = {"role": role}
        content = message.get("content")
        tool_calls = message.get("tool_calls")
        tool_call_id = message.get("tool_call_id")

        if role in {"system", "user"}:
            if content is None:
                continue
            simplified_message["content"] = content
        elif role == "assistant":
            if tool_calls:
                simplified_message["tool_calls"] = tool_calls
            if content is not None:
                simplified_message["content"] = content
            if "content" not in simplified_message and "tool_calls" not in simplified_message:
                continue
        elif role == "tool":
            if content is None or tool_call_id is None:
                continue
            simplified_message["content"] = content
            simplified_message["tool_call_id"] = tool_call_id

        simplified_messages.append(simplified_message)

    return simplified_messages


def extract_for_multimodal_training(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取成更贴近 SFT 的 messages 格式。
    若 messages 中存在 image_url，则自动补充 image_wh 并插入 <IMG_CONTEXT>。
    """
    normalized_messages = normalize_messages_for_multimodal_sft(data.get("messages", []))
    normalized_messages = _simplify_messages_for_sft(normalized_messages)
    new_data = {"messages": normalized_messages}

    tools = data.get("tools", [])
    if tools:
        new_data["tools"] = tools
        new_data["parallel_tool_calls"] = False

    return generate_id_to_data(new_data)


def _serialize_tool_calls_for_xtuner(tool_calls: Any) -> str:
    """将 OpenAI 风格 tool_calls 序列化为普通 assistant 文本。"""
    if not isinstance(tool_calls, list):
        return ""

    rendered_blocks: List[str] = []
    for tool_call in tool_calls:
        if not isinstance(tool_call, dict):
            continue

        function = tool_call.get("function", tool_call)
        if not isinstance(function, dict):
            continue

        name = function.get("name", "")
        arguments = function.get("arguments", "")
        if not name:
            continue

        if isinstance(arguments, str):
            args_str = arguments
        else:
            args_str = json.dumps(arguments, ensure_ascii=False)

        rendered_blocks.append(
            f'<tool_call>\n{{"name": "{name}", "arguments": {args_str}}}\n</tool_call>'
        )

    return "\n".join(rendered_blocks)


def _simplify_messages_for_xtuner_strict(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    转成可被 xtuner.v1.data_proto.messages.ChatMessages 接受的严格版本。
    仅输出 ChatMsg 支持的字段:
    - role
    - content
    - loss
    - thinking

    兼容 evaluator 产生的 tool 轨迹:
    - assistant.reasoning_content -> assistant.thinking
    - assistant.tool_calls -> 追加到 assistant.content
    - role == "tool" -> 改写为 user 的 <tool_response> 文本
    """
    simplified_messages: List[Dict[str, Any]] = []
    allowed_roles = {"system", "user", "assistant", "tool"}

    for message in messages:
        if not isinstance(message, dict):
            continue

        role = message.get("role")
        if role not in allowed_roles:
            continue

        content = message.get("content")
        simplified_message: Dict[str, Any]

        if role == "tool":
            if content is None:
                continue
            simplified_message = {
                "role": "user",
                "content": f"<tool_response>\n{content}\n</tool_response>",
                "loss": False,
            }
        else:
            simplified_message = {"role": role}
            tool_calls_text = _serialize_tool_calls_for_xtuner(message.get("tool_calls"))

            if role == "assistant":
                reasoning = message.get("reasoning_content")
                if isinstance(reasoning, str) and reasoning.strip():
                    simplified_message["thinking"] = reasoning

                if content is None and tool_calls_text:
                    content = tool_calls_text
                elif isinstance(content, str) and tool_calls_text:
                    content = f"{content}\n{tool_calls_text}" if content else tool_calls_text

            if content is None:
                continue

            simplified_message["content"] = content

            if "loss" in message:
                simplified_message["loss"] = message["loss"]
            elif role == "assistant":
                simplified_message["loss"] = True

        if len(simplified_message) == 1:
            continue

        simplified_messages.append(simplified_message)

    return simplified_messages


def _simplify_tools_for_xtuner_strict(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """仅保留 XTuner 工具定义所需字段。"""
    simplified_tools: List[Dict[str, Any]] = []

    for tool in tools:
        if not isinstance(tool, dict):
            continue
        tool_type = tool.get("type")
        function = tool.get("function")
        if tool_type is None or not isinstance(function, dict):
            continue
        simplified_tools.append({
            "type": tool_type,
            "function": function,
        })

    return simplified_tools


def extract_for_xtuner_strict_training(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    提取为 XTuner 严格字段格式。
    兼容纯文本和多模态；若存在 image_url，则自动补 image_wh 和 <IMG_CONTEXT>。
    """
    normalized_messages = normalize_messages_for_multimodal_sft(data.get("messages", []))
    new_data = {
        "messages": _simplify_messages_for_xtuner_strict(normalized_messages),
    }

    tools = _simplify_tools_for_xtuner_strict(data.get("tools", []))
    if tools:
        new_data["tools"] = tools

    return new_data

def generate_id_to_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """添加id到数据（基于内容的哈希值生成确定性id）"""
    # 使用消息内容生成确定性 id（相同内容生成相同id，便于去重）
    content = json.dumps(data.get("messages", []), sort_keys=True, ensure_ascii=False)
    content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
    new_data = {'id': content_hash}
    new_data.update(data)
    return new_data

def extract_assistant_responses(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    提取所有 assistant 的响应（一对多转换）
    
    Returns:
        每个 assistant 消息对应一个字典
    """
    messages = data.get("messages", [])
    assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
    
    return [
        {
            "index": idx,
            "content": msg.get("content"),
            "tool_calls": msg.get("tool_calls"),
            "data_source": data.get("input", {}).get("data_source"),
            "score": data.get("score", 0)
        }
        for idx, msg in enumerate(assistant_messages)
    ]


def create_field_extractor(*field_paths: str) -> Callable:
    """
    创建一个提取指定字段的转换函数
    
    Args:
        *field_paths: 要提取的字段路径（支持嵌套，用点号分隔）
    
    Returns:
        转换函数
    
    示例:
        # 提取多个字段
        extractor = create_field_extractor(
            "input.data_source",
            "score",
            "messages",
            "input.extra_info.generator_name"
        )
        processor.add_transformer(extractor)
    """
    def _get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """获取嵌套字段的值"""
        value = data
        for key in path.split('.'):
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value
    
    def _extract(data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for path in field_paths:
            # 使用路径的最后一部分作为键名
            key = path.split('.')[-1]
            result[key] = _get_nested_value(data, path)
        return result
    
    return _extract


def create_custom_transformer(transform_dict: Dict[str, Any]) -> Callable:
    """
    创建一个自定义转换函数，支持字段重命名和默认值
    
    Args:
        transform_dict: 转换配置字典
            键: 输出字段名
            值: 可以是:
                - str: 输入字段路径（支持嵌套）
                - tuple: (字段路径, 默认值)
                - callable: 自定义函数，接收原始数据返回字段值
    
    Returns:
        转换函数
    
    示例:
        transformer = create_custom_transformer({
            "text": "messages[-1].content",  # 提取最后一条消息的内容
            "source": "input.data_source",
            "gen": ("input.extra_info.generator_name", "unknown"),
            "final_score": lambda x: x.get("score", 0) * 100,
            "success": "success"
        })
    """
    def _get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
        """获取嵌套字段的值，支持列表索引"""
        value = data
        for key in path.split('.'):
            if isinstance(value, dict):
                value = value.get(key, default)
            elif isinstance(value, list) and key.startswith('[') and key.endswith(']'):
                try:
                    index = int(key[1:-1])
                    value = value[index] if -len(value) <= index < len(value) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default
        return value
    
    def _transform(data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for output_key, config in transform_dict.items():
            if callable(config):
                # 自定义函数
                result[output_key] = config(data)
            elif isinstance(config, tuple):
                # (路径, 默认值)
                path, default = config
                result[output_key] = _get_nested_value(data, path, default)
            elif isinstance(config, str):
                # 字段路径
                result[output_key] = _get_nested_value(data, config)
            else:
                # 直接使用配置值
                result[output_key] = config
        return result
    
    return _transform


# ============= 命令行接口 =============

def main():
    """命令行接口示例"""
    import argparse
    
    parser = argparse.ArgumentParser(description="数据后处理工具")
    parser.add_argument("input", help="输入 jsonl 文件路径")
    parser.add_argument("output", nargs='?', default=None, help="输出 jsonl 文件路径（可选，不提供则自动生成）")
    parser.add_argument("--filter-success", action="store_true", help="只保留成功的样本")
    parser.add_argument("--min-score", type=float, default=0.9, help="最小分数")
    parser.add_argument("--max-score", type=float, default=1.0, help="最大分数")
    parser.add_argument("--data-source", type=str, help="按数据源过滤")
    parser.add_argument("--filter-design-end", action="store_true", help="只保留最后一条消息包含 <Design End> 的样本")
    parser.add_argument("--extract-training", action="store_true", help="提取训练数据格式")
    parser.add_argument("--extract-multimodal-training", action="store_true", help="提取多模态 SFT 训练格式")
    parser.add_argument("--extract-xtuner-strict-training", action="store_true", help="提取 XTuner 严格字段训练格式")
    parser.add_argument("--extract-messages", action="store_true", help="只提取消息")
    parser.add_argument("--expand-messages-prefixes", action="store_true", help="将多轮对话展开为前缀集")
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = DataPostProcessor()
    
    # 添加过滤器
    if args.filter_success:
        processor.add_filter(filter_by_success, name="success")
    
    if args.min_score > 0.0 or args.max_score < 1.0:
        processor.add_filter(filter_by_score(args.min_score, args.max_score), name="score")
    
    if args.data_source:
        processor.add_filter(filter_by_data_source(args.data_source), name="data_source")
    
    if args.filter_design_end:
        processor.add_filter(filter_by_design_end, name="design_end")
    
    # 添加转换器(需要按顺序添加，因为有些转换函数会修改数据)
    if args.expand_messages_prefixes:
        processor.add_transformer(expand_messages_prefixes, name="expand_messages_prefixes")
    if args.extract_training:
        processor.add_transformer(extract_for_training, name="training_format")
    if args.extract_multimodal_training:
        processor.add_transformer(extract_for_multimodal_training, name="multimodal_training_format")
    if args.extract_xtuner_strict_training:
        processor.add_transformer(extract_for_xtuner_strict_training, name="xtuner_strict_training_format")
    if args.extract_messages:
        processor.add_transformer(extract_messages_only, name="messages_only")

    
    # 执行处理
    processor.process(args.input, args.output)


if __name__ == "__main__":
    main()


"""
示例用法:

# 方式1: 不指定输出路径，自动生成 (例如: eval_results_20251027171406_processed.jsonl)
python -m internbootcamp.utils.data_postprocess \
    ${PROJECT_DIR} \
    --extract-training \
    --min-score 0.9 \
    --max-score 1.0

# 方式2: 指定输出路径
python -m internbootcamp.utils.data_postprocess \
    Bootcampv2/example_bootcamp/data/eval_output/deepseekv3-1-terminus/eval_results_20251027171406.jsonl \
    Bootcampv2/example_bootcamp/data/eval_output/deepseekv3-1-terminus/eval_results_custom.jsonl \
    --expand-messages-prefixes \
    --min-score 0.9 \
    --max-score 1.0

python -m internbootcamp.utils.data_postprocess \
    ${PROJECT_DIR} \
    internbootcamp/bootcamps/AnalogCircuitSizing/data/bayesian_agent_rft_1230_train.jsonl \
    --filter-design-end \
    --extract-training \
    --min-score 0.0 \
    --max-score 1.0

${PROJECT_DIR}
"""
