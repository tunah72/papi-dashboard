"""Plugin registry cho các AI technique. Mỗi plugin trong app/ai/techniques/ gọi register()
khi được import. Trang AI Assistant gọi discover() để nạp toàn bộ plugin rồi liệt kê.

Giao diện plugin: mỗi technique cung cấp key, label, description, và default_request
(một câu yêu cầu ngôn ngữ tự nhiên seed cho api_ai)."""
import importlib
import pkgutil

_REGISTRY = {}


def register(key: str, label: str, description: str, 
             default_request: str = "", 
             user_prompt: str = "", 
             system_instruction: str = ""):
    # Hỗ trợ backward compatibility (nếu plugin chưa được cập nhật)
    actual_user_prompt = user_prompt if user_prompt else default_request

    _REGISTRY[key] = {
        "key": key, 
        "label": label,
        "description": description, 
        "default_request": actual_user_prompt,
        "user_prompt": actual_user_prompt,
        "system_instruction": system_instruction
    }


def discover():
    """Import mọi module trong app/ai/techniques/ để chúng tự đăng ký."""
    import ai.techniques as pkg
    for m in pkgutil.iter_modules(pkg.__path__):
        importlib.import_module(f"ai.techniques.{m.name}")


def all_techniques() -> list:
    return list(_REGISTRY.values())


def get(key: str) -> dict:
    return _REGISTRY[key]
