import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import argparse

# --- Configuration ---
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".md": "markdown",
    ".txt": "",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".java": "java",
    ".sh": "bash",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".rb": "ruby",
    ".php": "php",
    ".sql": "sql",
    ".go": "go",
    ".rs": "rust",
    ".swift": "swift",
}

# --- Functions ---
def get_directory_path_gui():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askdirectory(title="Select Directory")

def get_extensions_gui():
    root = tk.Tk()
    root.withdraw()
    extensions = simpledialog.askstring("Extensions", "Enter comma-separated file extensions (e.g., .txt,.md):")
    if extensions:
        return [ext.strip().lower() for ext in extensions.split(',')]
    return []

def get_save_location(default_name):
    root = tk.Tk()
    root.withdraw()
    return filedialog.asksaveasfilename(
        defaultextension=".md",
        initialfile=f"{default_name}.md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
        title="Save Output As"
    )

def build_tree_structure(files):
    tree = {}
    for file_path in files:
        parts = file_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[parts[-1]] = None  # mark as a file
    return tree

def print_tree(tree, prefix="", is_last=True):
    output = ""
    entries = list(tree.keys())
    for i, name in enumerate(entries):
        is_last_entry = (i == len(entries) - 1)
        if is_last_entry:
            connector = "└── "
            extended_prefix = prefix + "    "
        else:
            connector = "├── "
            extended_prefix = prefix + "│   "

        output += f"{prefix}{connector}{name}\n"

        if tree[name] is not None:  # It's a folder
            output += print_tree(tree[name], extended_prefix, is_last=is_last_entry)
    return output

def generate_markdown_output(root, files):
    result = "\n---\n"
    for file in files:
        full_path = os.path.join(root, file)
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            content = f"[Error reading file: {str(e)}]"

        _, ext = os.path.splitext(file)
        lang = ext.lower()
        if lang in EXTENSION_TO_LANGUAGE:
            lang = EXTENSION_TO_LANGUAGE[lang]

        result += f"\n## {file}\n\n"
        result += f"```{lang}\n"
        result += content
        result += "\n```\n"
    return result

def get_extensions_from_input(extensions_str):
    if extensions_str:
        return [ext.strip().lower() for ext in extensions_str.split(',')]
    return []

def main():
    parser = argparse.ArgumentParser(description="Generate a Markdown file with code snippets and directory tree.")
    parser.add_argument("-i", "--input", help="Input directory path (bypass GUI)")
    parser.add_argument("-e", "--extensions", help="Comma-separated list of file extensions (e.g., .py,.md)")
    args = parser.parse_args()

    # Determine directory
    if args.input:
        directory = os.path.abspath(args.input)
        if not os.path.isdir(directory):
            print(f"Error: '{directory}' is not a valid directory.")
            return
    else:
        directory = get_directory_path_gui()
        if not directory:
            print("No directory selected.")
            return

    # Determine extensions
    if args.extensions:
        extensions = get_extensions_from_input(args.extensions)
    else:
        extensions = get_extensions_gui()
    if not extensions:
        print("No extensions provided.")
        return

    # Find matching files
    matched_files = []
    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                rel_path = os.path.relpath(os.path.join(root_dir, file), directory)
                matched_files.append(rel_path)

    if not matched_files:
        print("No matching files found.")
        return

    # Generate Tree View
    tree_structure = build_tree_structure(matched_files)
    tree_output = ".\n" + print_tree(tree_structure)

    # Generate Markdown Content
    root_name = os.path.basename(os.path.abspath(directory))
    markdown_content = (
        f"# {root_name}\n\n"
        f"{tree_output}"
        f"{generate_markdown_output(directory, matched_files)}"
    )

    # Save location
    if args.input:
        # Auto-generate save path if input given (e.g., /path/to/project.md)
        default_save = os.path.join(os.path.dirname(directory), f"{root_name}.md")
        save_path = default_save
        # Optional: you could still ask for save location, but for CLI we auto-save
        # Or prompt only if you want — here we auto-save
    else:
        save_path = get_save_location(root_name)
        if not save_path:
            print("Save operation canceled.")
            return

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"File saved successfully to: {save_path}")
    except Exception as e:
        print(f"Failed to save file: {e}")

if __name__ == "__main__":
    main()
