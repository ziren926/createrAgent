import yaml

def load_config(file_path: str):
    """
    加载 YAML 配置文件。

    Args:
        file_path (str): YAML 文件路径。
    Returns:
        dict: 配置字典。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"配置文件 {file_path} 未找到！")
        return {}
    except yaml.YAMLError as e:
        print(f"加载 YAML 文件时出错: {e}")
        return {}