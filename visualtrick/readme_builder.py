import os
import html
import subprocess
from datetime import datetime


def detect_project_goal(repo_data):
    if not repo_data.get("files"):
        return "General Python Project"

    requirements = repo_data.get("requirements", [])

    if any("fastapi" in r.lower() for r in requirements):
        return "FastAPI Backend Service"

    if any("flask" in r.lower() for r in requirements):
        return "Flask Web Application"

    if any(("torch" in r.lower()) or ("tensorflow" in r.lower()) for r in requirements):
        return "Machine Learning Project"

    if any("django" in r.lower() for r in requirements):
        return "Django Web Application"

    if any("streamlit" in r.lower() for r in requirements):
        return "Streamlit Data App"

    return "Python Application"


def detect_github_pages_url(target_path: str):
    try:
        remote = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=target_path,
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        if "github.com" not in remote:
            return None

        if remote.endswith(".git"):
            remote = remote[:-4]

        if remote.startswith("git@github.com:"):
            repo_part = remote.split("git@github.com:")[1]
        elif remote.startswith("https://github.com/"):
            repo_part = remote.split("https://github.com/")[1]
        else:
            return None

        username, repo = repo_part.split("/", 1)
        return f"https://{username}.github.io/{repo}/architecture.html"

    except Exception:
        return None


def analyze_file_types(files):
    """
    Count files by extension.

    `files` is expected to be a list of relative paths (strings) as produced
    by the fixed scan_repository() — e.g. "src/main.py", "static/app.js".
    TypeScript declaration files (.d.ts) are excluded from the TS count.
    """
    stats = {
        "python": 0,
        "html":   0,
        "css":    0,
        "js":     0,
        "ts":     0,
        "react":  0,
        "json":   0,
    }

    for f in files:
        f_low = f.lower()

        if f_low.endswith(".py"):
            stats["python"] += 1
        elif f_low.endswith(".html"):
            stats["html"] += 1
        elif f_low.endswith(".css"):
            stats["css"] += 1
        elif f_low.endswith(".js"):
            stats["js"] += 1
        elif f_low.endswith(".tsx") or f_low.endswith(".jsx"):
            # Check React before .ts so ".tsx" is not double-counted
            stats["react"] += 1
        elif f_low.endswith(".ts") and not f_low.endswith(".d.ts"):
            stats["ts"] += 1
        elif f_low.endswith(".json"):
            stats["json"] += 1

    return stats


def generate_readme(repo_data, target_path: str, arch_path: str):
    # Always use docs/architecture.html as the canonical output path
    rel_arch = "docs/architecture.html"
    has_arch_file = os.path.exists(os.path.join(target_path, "docs", "architecture.html"))

    github_pages_url = detect_github_pages_url(target_path)
    arch_link = github_pages_url if github_pages_url else rel_arch

    files = repo_data.get("files", [])
    requirements_list = repo_data.get("requirements", [])
    goal = detect_project_goal(repo_data)
    stats = analyze_file_types(files)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Build file statistics table — only emit rows for types that actually exist
    file_stats_rows = []

    if stats.get("python", 0) > 0:
        file_stats_rows.append(f"| 🐍 Python Files | {stats['python']} |")
    if stats.get("html", 0) > 0:
        file_stats_rows.append(f"| 🌐 HTML Files | {stats['html']} |")
    if stats.get("css", 0) > 0:
        file_stats_rows.append(f"| 🎨 CSS Files | {stats['css']} |")
    if stats.get("js", 0) > 0:
        file_stats_rows.append(f"| ⚡ JavaScript Files | {stats['js']} |")
    if stats.get("ts", 0) > 0:
        file_stats_rows.append(f"| 🔷 TypeScript Files | {stats['ts']} |")
    if stats.get("react", 0) > 0:
        file_stats_rows.append(f"| ⚛️ React Files (JSX/TSX) | {stats['react']} |")
    if stats.get("json", 0) > 0:
        file_stats_rows.append(f"| 📋 JSON Files | {stats['json']} |")

    arch_count = 1 if has_arch_file else 0
    file_stats_rows.append(f"| 🗺️ Architecture Files | {arch_count} |")

    req_detected = f"✅ Yes — {len(requirements_list)} packages" if requirements_list else "⚠️ No"
    file_stats_rows.append(f"| 📦 Requirements Detected | {req_detected} |")

    file_stats_table = "\n".join(file_stats_rows)

    # Requirements section
    if requirements_list:
        requirements_md = "```txt\n" + "\n".join(r.strip() for r in requirements_list if r.strip()) + "\n```"
        setup_instructions = """```bash
pip install -r requirements.txt
```"""
    else:
        requirements_md = "> ⚠️ **Note:** No `requirements.txt` detected. Add one for dependency tracking."
        setup_instructions = "> ⚠️ **Note:** No requirements.txt found — nothing to install."

    # GitHub Pages URL
    if github_pages_url:
        pages_url_display = github_pages_url
        pages_badge = "![Auto-detected](https://img.shields.io/badge/Status-Auto--detected-success?style=flat-square)"
        pages_note = "*Detected from your git remote configuration.*"
    else:
        pages_url_display = "https://&lt;your-username&gt;.github.io/&lt;your-repo&gt;/architecture.html"
        pages_badge = "![Manual Setup](https://img.shields.io/badge/Status-Manual%20Setup%20Needed-blue?style=flat-square)"
        pages_note = "*Replace `<your-username>` and `<your-repo>` with your GitHub values.*"

    markdown_content = f"""<div align="center">

# 🚀 AI Generated Project Report

**Automated repository intelligence powered by VisualTrick**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Enabled-success?style=flat-square&logo=github)]({arch_link})
[![Python](https://img.shields.io/badge/Python-Analysis-blue?style=flat-square&logo=python)](.)
[![Documentation](https://img.shields.io/badge/Docs-Auto--Generated-informational?style=flat-square)](./docs/architecture.html)

</div>

---

## 🎯 Project Goal

> **{goal}**

---

## 📊 Repository Overview

| Metric | Value |
|--------|-------|
{file_stats_table}
| 🔍 Scan Scope | Local repository analysis |

---

## 📦 Requirements

{requirements_md}

---

## ⚙️ Setup Instructions

{setup_instructions}

---

## ▶️ Usage

Follow these steps to generate and deploy your architecture visualization:

### **1️⃣ Generate the Architecture Graph**

```bash
visualtrick .
```

This will analyze your codebase and create an interactive dependency graph.

### **2️⃣ Commit and Push**

```bash
git add docs/architecture.html README.md
git commit -m "chore: add architecture graph"
git push
```

### **3️⃣ Enable GitHub Pages**

Follow the one-time setup instructions below to make your graph accessible online.

---

## 🌐 GitHub Pages — Live Architecture Graph

VisualTrick writes the graph into the `docs/` folder so it can be served directly via GitHub Pages with zero extra configuration.

### ✅ One-Time Repository Setup

1. Go to your repository on GitHub → click **Settings**
2. In the left sidebar, click **Pages**
3. Under **Source**, configure:
   - **Deploy from**: branch
   - **Branch**: `main`
   - **Folder**: `/docs`
4. Click **Save**
5. Wait **~30–60 seconds** for GitHub to build your site 🎉

### 🔗 Live Graph URL

{pages_badge}

{pages_note}

**Your architecture graph will be available at:**

```
{pages_url_display}
```

[**🔗 Open Interactive Architecture Graph →**]({arch_link})

---

## 🧠 Architecture Intelligence

VisualTrick performed static analysis of all module imports and relationships in this repository, then generated an interactive dependency graph saved to `docs/architecture.html`.

**Features:**
- 📊 Visual dependency mapping
- 🔍 Interactive module exploration
- 📈 Import relationship tracking
- 🎯 Bottleneck identification

Open it locally in your browser, or access it live via GitHub Pages after completing the setup above.

---

## 📁 Generated Artifacts

| File | Description |
|------|-------------|
| `docs/architecture.html` | Interactive dependency graph — served via GitHub Pages |
| `README.md` | Auto-generated project documentation (this file) |

---

## ⚠️ Important Notes

> 📌 **Manual Review Recommended**  
> This report is auto-generated via static analysis. Please review for accuracy.

> 🔄 **Dynamic Imports**  
> Dynamic imports and runtime dependencies may not be fully detected.

> 📦 **Best Practices**  
> For optimal results, ensure `requirements.txt` is present and up to date.

> 🚀 **Deployment**  
> Remember to commit and push the `docs/` folder to enable GitHub Pages serving.

---

<div align="center">

**Generated by VisualTrick** · {timestamp}

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg?style=flat-square&logo=python)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/View%20on-GitHub-181717.svg?style=flat-square&logo=github)](.)

</div>"""

    md_path = os.path.join(target_path, "README.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"README generated: {md_path}")
    