import os
import ast


def scan_repository(path):
    repo_data = {
        "files": [],
        "imports": {},
        "requirements": [],
        "internal_modules": set(),
        "import_stats": {"internal": 0, "external": 0},
        "functions": {},
        "calls": [],
        "entry_points": []
    }

    SKIP_DIRS = {
        "__pycache__", "node_modules", ".git",
        "venv", ".venv", "env", "dist", "build", ".mypy_cache"
    }

    NON_PY_EXTS = {".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".json"}

    py_files = []

    # ---------- collect ALL files ----------
    for root, dirs, files in os.walk(path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]

        for file in files:
            full_path = os.path.join(root, file)
            rel_path  = os.path.relpath(full_path, path)
            ext       = os.path.splitext(file)[1].lower()

            # Always add to the flat file list (used by analyze_file_types)
            repo_data["files"].append(rel_path)

            if ext == ".py":
                py_files.append(full_path)
                module_name = os.path.splitext(file)[0]
                repo_data["internal_modules"].add(module_name)

    # ---------- analyze each Python file ----------
    for file_path in py_files:
        imports, functions, calls, has_main = analyze_file(file_path)

        repo_data["imports"][file_path] = imports
        repo_data["functions"][file_path] = functions
        repo_data["calls"].extend(calls)

        if has_main:
            repo_data["entry_points"].append(os.path.basename(file_path))

    # ---------- classify imports ----------
    for imports in repo_data["imports"].values():
        for imp in imports:
            base = imp.split(".")[0]
            if base in repo_data["internal_modules"]:
                repo_data["import_stats"]["internal"] += 1
            else:
                repo_data["import_stats"]["external"] += 1

    # ---------- requirements ----------
    req_path = os.path.join(path, "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r", encoding="utf-8") as f:
            repo_data["requirements"] = [
                line.strip()
                for line in f.read().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]

    return repo_data


def analyze_file(file_path):
    imports = []
    functions = []
    calls = []
    has_main = False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            # imports
            if isinstance(node, ast.Import):
                for n in node.names:
                    imports.append(n.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

            # functions
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)

            # function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)

            # entry point detection
            elif isinstance(node, ast.If):
                try:
                    if (
                        isinstance(node.test, ast.Compare)
                        and isinstance(node.test.left, ast.Name)
                        and node.test.left.id == "__name__"
                    ):
                        has_main = True
                except Exception:
                    pass

    except Exception:
        pass

    return imports, functions, calls, has_main