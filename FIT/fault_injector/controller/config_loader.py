import yaml
import os

def load_presets(file="config/presets.yaml"):
    try:
        with open(file, 'r') as f:
            return yaml.safe_load(f)["presets"]
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return {}

def save_custom(name, config, file="config/presets.yaml"):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    data = load_presets(file)
    data[name] = config
    with open(file, 'w') as f:
        yaml.dump({"presets": data}, f)
    print(f" Preset '{name}' saved.")

