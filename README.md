# 📊 Universal Codebase Analyzer

A powerful, zero-dependency Python script that generates comprehensive codebase analysis files for any project. Perfect for understanding project structure and providing context to AI assistants.
Help your AI agent understand your project's codebase without depending on their codebase analysis capability.

## 🚀 Features

- **Zero dependencies** - Works with just Python's standard library
- **Cross-platform** - Runs on Windows, macOS, and Linux
- **Universal compatibility** - Works with any programming language or project structure
- **Git integration** - Provides repository insights when available
- **Intelligent filtering** - Automatically ignores non-project files and directories
- **Comprehensive analysis** - Generates multiple helpful reports

## 📥 Installation

Just download the single Python file:

```bash
# Using curl
curl -o codebase_analyzer.py https://raw.githubusercontent.com/username/repo/main/codebase_analyzer.py

# Or simply copy the script to a file named codebase_analyzer.py in your project root
```

## 🛠️ Usage

Run the script from your project root directory:

```bash
python codebase_analyzer.py
```

That's it! No configuration needed. The script will analyze your codebase and generate reports in a `00_docs` folder.

## 📄 Generated Files

The analyzer creates five detailed files in the `00_docs` directory:

1. **project_summary.md** - Overview of your project with statistics and Git information
   - Repository details, file counts, language breakdown
   - Directory statistics and top folders by file count

2. **codebase_structure.txt** - Complete listing of all project files
   - Hierarchical view of your entire codebase

3. **largest_files.txt** - Top 20 files by line count
   - Helps identify core logic files and potential refactoring targets

4. **recent_files.txt** - 20 most recently modified files
   - Shows what's actively being worked on

5. **folder_summary.txt** - Statistics for each folder
   - File counts and line counts broken down by directory

## 🤖 Using With AI Assistants

This tool is especially helpful when working with AI coding assistants:

1. Run the analyzer before your session
2. Point the AI to the `00_docs` folder first
3. Ask it to review the `project_summary.md` for context
4. Refer to the specific files you're working on

This gives AI assistants crucial context about your codebase, helping them provide more relevant assistance.

## ⚙️ Customization (Optional)

The script works out of the box for most projects, but you can customize:

- **Ignored directories**: By default, skips `.git`, `node_modules`, `venv`, etc.
- **Text file extensions**: Recognizes common programming languages and text formats

To customize, open the script and modify the `ignore_dirs` or `text_extensions` lists in the `__init__` method.

## 🔍 Compatibility

- **Python**: Works with Python 3.6+ (no external dependencies)
- **Languages**: Analyzes any programming language
- **Project size**: Efficiently handles small to large codebases
- **Git**: Enhanced with Git information when available, but works without Git

## 📝 License

MIT License - Feel free to use, modify, and share!

## 🤝 Contributing

Contributions welcome! Feel free to open issues or submit pull requests.
