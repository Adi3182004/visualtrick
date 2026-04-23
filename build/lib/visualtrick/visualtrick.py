import os
import argparse
from .analyzer import scan_repository
from .graph_builder import build_graph
from .readme_builder import generate_readme

def run(target_path: str):
    target_path = os.path.abspath(target_path)
    repo_data = scan_repository(target_path)
    arch_path = build_graph(repo_data, target_path)
    generate_readme(repo_data, target_path, arch_path)
    print("VisualTrick completed successfully")

def main():
    parser = argparse.ArgumentParser(description="VisualTrick Repo Intelligence Tool")
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    run(args.path)

if __name__ == "__main__":
    main()