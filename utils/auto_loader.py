"""
Auto Loader — tools/ folder me koi bhi naya file daalo,
usme register(app) function rakho, automatically load ho jayega.
Manual CommandHandler add karne ki zarurat nahi.
"""

import os
import importlib
import pkgutil
import traceback


def load_tools(app):
    """tools/ folder se saari files auto-load karta hai."""
    tools_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tools")
    loaded = []

    for finder, name, ispkg in pkgutil.iter_modules([tools_path]):
        if name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"tools.{name}")
            if hasattr(module, "register"):
                module.register(app)
                loaded.append(name)
                print(f"✅ Tool loaded: {name}")
            else:
                print(f"⚠️  Tool skipped (no register): {name}")
        except Exception as e:
            print(f"❌ Tool failed [{name}]: {e}")
            traceback.print_exc()

    print(f"📦 Total tools loaded: {len(loaded)}")
    return loaded


def load_modules(app):
    """modules/ folder se core modules load karta hai."""
    modules_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "modules")
    loaded = []

    # Order matter karta hai — important modules pehle
    priority = ["start", "help", "chat", "admin", "owner", "image", "fonts", "moderation"]

    # Pehle priority wale
    for name in priority:
        try:
            module = importlib.import_module(f"modules.{name}")
            if hasattr(module, "register"):
                module.register(app)
                loaded.append(name)
                print(f"✅ Module loaded: {name}")
        except ModuleNotFoundError:
            pass
        except Exception as e:
            print(f"❌ Module failed [{name}]: {e}")
            traceback.print_exc()

    # Baaki modules
    for finder, name, ispkg in pkgutil.iter_modules([modules_path]):
        if name.startswith("_") or name in loaded:
            continue
        try:
            module = importlib.import_module(f"modules.{name}")
            if hasattr(module, "register"):
                module.register(app)
                loaded.append(name)
                print(f"✅ Module loaded: {name}")
        except Exception as e:
            print(f"❌ Module failed [{name}]: {e}")
            traceback.print_exc()

    print(f"📦 Total modules loaded: {len(loaded)}")
    return loaded
