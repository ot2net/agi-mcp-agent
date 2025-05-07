#!/usr/bin/env python3
"""
从pyproject.toml文件生成requirements.txt文件的脚本。
适用于不使用Poetry的环境，例如Docker部署。
"""

import toml
import sys
from pathlib import Path

def generate_requirements(pyproject_path, output_path, include_dev=False):
    """
    从pyproject.toml生成requirements.txt
    
    Args:
        pyproject_path: pyproject.toml文件的路径
        output_path: 输出的requirements.txt文件路径
        include_dev: 是否包含开发依赖
    """
    try:
        # 加载pyproject.toml
        pyproject = toml.load(pyproject_path)
        
        # 获取依赖
        dependencies = pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})
        
        # 删除python依赖，因为它通常指定了Python版本而不是包
        if 'python' in dependencies:
            del dependencies['python']
        
        # 处理开发依赖
        dev_dependencies = {}
        if include_dev:
            dev_dependencies = pyproject.get('tool', {}).get('poetry', {}).get('group', {}).get('dev', {}).get('dependencies', {})
        
        # 合并依赖
        all_dependencies = {**dependencies, **dev_dependencies}
        
        # 格式化依赖为pip格式
        pip_dependencies = []
        for package, version in all_dependencies.items():
            if isinstance(version, str):
                # 将Poetry的版本规范转换为pip格式
                version = version.replace('^', '>=')
                pip_dependencies.append(f"{package}{version}")
            elif isinstance(version, dict):
                # 处理复杂的依赖说明
                if 'version' in version:
                    v = version['version'].replace('^', '>=')
                    pip_dependencies.append(f"{package}{v}")
                else:
                    # 如果没有版本指定，仅添加包名
                    pip_dependencies.append(package)
        
        # 写入requirements.txt
        with open(output_path, 'w') as f:
            f.write('\n'.join(pip_dependencies))
        
        print(f"成功生成 {output_path}")
        return True
        
    except Exception as e:
        print(f"生成requirements.txt失败: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    pyproject_path = Path("pyproject.toml")
    output_path = Path("requirements.txt")
    
    # 检查命令行参数
    include_dev = "--dev" in sys.argv
    
    if not pyproject_path.exists():
        print(f"错误: {pyproject_path} 不存在", file=sys.stderr)
        sys.exit(1)
    
    success = generate_requirements(pyproject_path, output_path, include_dev)
    sys.exit(0 if success else 1)