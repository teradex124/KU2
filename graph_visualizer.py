import argparse
import os
import graphviz
import xml.etree.ElementTree as etree
from typing import Dict, List

def get_dependencies(package_name: str, max_depth: int, current_depth: int = 0, visited: Dict[str, List[str]] = None) -> \
Dict[str, List[str]]:

    if visited is None:
        visited = {}

    if current_depth > max_depth or package_name in visited:
        return visited

    nuspec_path = f"./NewtonsoftJSON/Newtonsoft.Json.nuspec"
    if not os.path.exists(nuspec_path):
        print(f"Файл {nuspec_path} не найден. Пропуск...")
        visited[package_name] = []
        return visited

    tree = etree.parse(nuspec_path)
    root = tree.getroot()

    ns = {"default": "http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd"}
    dependencies = []
    for dependency in root.findall(".//default:dependency", ns):
        dep_id = dependency.get("id")
        if dep_id:
            dependencies.append(dep_id)

    print(f"Анализируем зависимости для пакета: {package_name}: {dependencies}")

    visited[package_name] = dependencies

    for dep in dependencies:
        get_dependencies(dep, max_depth, current_depth + 1, visited)

    return visited

def generate_graph(dependencies: Dict[str, List[str]], output_path: str):

    graph = graphviz.Digraph(format='png')

    for package, deps in dependencies.items():
        for dep in deps:
            graph.edge(package, dep)

    graph.render(output_path, cleanup=True)
    print(f"Граф зависимостей сохранен в {output_path}.png")

def main():
    parser = argparse.ArgumentParser(description="Инструмент для визуализации графа зависимостей .NET пакетов")
    parser.add_argument("--graphviz-path", required=True, help="Путь к программе Graphviz (dot)")
    parser.add_argument("--package-name", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--output-path", required=True, help="Путь к файлу с изображением графа зависимостей")
    parser.add_argument("--max-depth", type=int, required=True, help="Максимальная глубина анализа зависимостей")
    parser.add_argument("--repository-url", required=True, help="URL репозитория для анализа зависимостей")

    args = parser.parse_args()

    os.environ["PATH"] += os.pathsep + args.graphviz_path

    try:
        dependencies = get_dependencies(
            package_name=args.package_name,
            max_depth=args.max_depth
        )
        generate_graph(dependencies, args.output_path)
        print("Визуализация графа зависимостей успешно завершена.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()