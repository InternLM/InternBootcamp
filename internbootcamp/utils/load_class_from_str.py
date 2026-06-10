import importlib

def load_class_from_string(class_path: str):
    """
    从字符串路径动态加载类
    
    Args:
        class_path: 类的完整路径，如 'internbootcamp.bootcamps.example_bootcamp.example_evaluator.ExampleEvaluator'
        
    Returns:
        加载的类对象
    """
    try:
        module_path, class_name = class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except Exception as e:
        raise ImportError(f"无法加载类 {class_path}: {str(e)}")
 