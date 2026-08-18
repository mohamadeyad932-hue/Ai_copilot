import json
from pathlib import Path
from typing import Any, Optional


def write_json(file_path: Path, data: Any) -> bool:
    """كتابة أي نوع من البيانات إلى ملف JSON بأمان."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except (TypeError, ValueError) as e:
        print(f"خطأ: البيانات المدخلة غير قابلة للتحويل إلى JSON: {e}")
        return False
    except (PermissionError, OSError) as e:
        print(f"خطأ أثناء الكتابة في {file_path}: {e}")
        return False


def read_json(file_path: Path) -> Optional[Any]:
    """قراءة وتحليل البيانات من ملف JSON."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"خطأ: الملف '{file_path}' غير موجود.")
    except json.JSONDecodeError:
        print(f"خطأ: الملف '{file_path}' يحتوي على صيغة JSON غير صالحة.")
    except PermissionError:
        print(f"خطأ: ليس لديك صلاحية للوصول إلى '{file_path}'.")
    except OSError as e:
        print(f"حدث خطأ غير متوقع في النظام: {e}")
    return None
