import yaml

from typing import Any, Callable, Dict, List, Tuple
import importlib
from verl.tools.schemas import OpenAIFunctionToolSchema

def load_tool_from_config(tool_config: dict) -> Tuple[str, Callable[[str, dict], Any], Dict[str, Any]]:
    """
    根据 YAML 配置动态加载工具类并实例化。

    Args:
        tool_config (dict): 工具配置，必须包含:
            - class_name (str): 工具类的完整模块路径，如 'mytools.amplifier.CalcAmplifierGainTool'
            - tool_schema (dict): 符合 OpenAI 工具格式的 schema 定义（字典）
            - config (dict, optional): 传递给工具类初始化的参数

    Returns:
        tuple[str, Callable, dict]:
            - function_name: 工具函数名（用于匹配 LLM 输出）
            - execute_wrapper: 一个可调用对象，封装了 instance.execute，适配 function calling 接口
            - instance: 工具实例

    Raises:
        ImportError: 如果类无法加载、schema 验证失败或实例化出错
    """
    # print(tool_config)
    class_path = tool_config["class_name"]
    raw_schema = tool_config["tool_schema"]
    config = tool_config.get("config", {})

    # === 1. 验证并构造 OpenAIFunctionToolSchema 实例 ===
    try:
        validated_schema = OpenAIFunctionToolSchema(**raw_schema)
    except Exception as e:
        raise ImportError(f"Invalid tool schema: does not conform to OpenAIFunctionToolSchema. Error: {e}")

    function_name = validated_schema.function.name

    # === 2. 动态导入类 ===
    try:
        *modules, class_name = class_path.split(".")
        module_path = ".".join(modules)
        module = importlib.import_module(module_path)
        tool_class = getattr(module, class_name)
    except ImportError as e:
        raise ImportError(f"Failed to import module '{module_path}': {e}")
    except AttributeError:
        raise ImportError(f"Module '{module_path}' has no class '{class_name}'")

    # === 3. 实例化工具（传入 config 和 OpenAIFunctionToolSchema 实例）===
    try:
        instance = tool_class(config=config, tool_schema=validated_schema)
    except TypeError as e:
        raise ImportError(
            f"Failed to instantiate {class_path}. "
            f"Make sure it inherits from BaseTool and accepts (config, tool_schema: OpenAIFunctionToolSchema). Error: {e}"
        )

    # === 4. 返回：函数名、schema 字典、实例===
    return function_name, raw_schema, instance

def load_tool_from_config_path(tool_config_path: str) -> List[Tuple[str, Callable[[str, dict], Any], Dict[str, Any]]]:
    """
    从 YAML 配置文件路径加载工具配置列表并实例化所有工具。

    Args:
        tool_config_path (str): YAML 配置文件的路径，文件应包含 'tools' 键，其值为工具配置列表

    Returns:
        List[tuple[str, Callable, dict]]: 工具配置列表，每个元素包含:
            - function_name: 工具函数名（用于匹配 LLM 输出）
            - execute_wrapper: 一个可调用对象，封装了 instance.execute，适配 function calling 接口
            - instance: 工具实例

    Raises:
        FileNotFoundError: 如果配置文件不存在
        yaml.YAMLError: 如果 YAML 文件格式错误
        KeyError: 如果 YAML 文件中缺少 'tools' 键
        ImportError: 如果工具类无法加载或实例化失败
    """
    try:
        with open(tool_config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Tool config file not found: {tool_config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML config file '{tool_config_path}': {e}")
    
    # 检查是否包含 tools 键
    if 'tools' not in config_data:
        raise KeyError(f"YAML config file '{tool_config_path}' must contain a 'tools' key")
    
    tools_config = config_data['tools']
    if not isinstance(tools_config, list):
        raise ValueError(f"'tools' key in '{tool_config_path}' must contain a list of tool configurations")
    
    # 加载所有工具
    loaded_tools = []
    for tool_config in tools_config:
        tool_result = load_tool_from_config(tool_config)
        loaded_tools.append(tool_result)
    
    return loaded_tools

if __name__ == "__main__":
    import pprint
    
    tool_config_path = 'Bootcampv2/Retro/configs/retro_tool_config.yaml'
    print(f"正在加载工具配置: {tool_config_path}")
    try:
        tools = load_tool_from_config_path(tool_config_path)
        print(f"共加载 {len(tools)} 个工具:")
        for idx, (func_name, raw_schema, instance) in enumerate(tools):
            print(f"\n工具{idx+1}:")
            print(f"  函数名: {func_name}")
            print(f"  Schema:")
            pprint.pprint(raw_schema)
            print(f"  实例类型: {type(instance)}")
    except Exception as e:
        import traceback
        
    