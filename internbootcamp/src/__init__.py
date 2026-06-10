import pkgutil
import importlib



__all__ = []

# 自动导入子模块 + 提升 __all__ 中的内容
for importer, modname, ispkg in pkgutil.iter_modules(__path__, __name__ + "."):
    if ispkg:
        try:
            module = importlib.import_module(modname)
            module_name = modname.split(".")[-1]
            globals()[module_name] = module
            __all__.append(module_name)

            # 自动提升子模块中 __all__ 定义的符号
            if hasattr(module, '__all__'):
                for name in module.__all__:
                    if hasattr(module, name):
                        attr = getattr(module, name)
                        globals()[name] = attr
                        __all__.append(name)
        except ImportError as e:
            print(f"[Warning] Failed to import {modname}: {e}")