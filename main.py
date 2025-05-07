import os
import tkinter as tk
from tkinter import filedialog, simpledialog

def get_directory_path():
    root = tk.Tk()
    root.withdraw()  # Hide main window
    directory = filedialog.askdirectory(title="Select Directory")
    return directory

def get_extensions():
    root = tk.Tk()
    root.withdraw()
    extensions = simpledialog.askstring("Extensions", "Enter comma-separated file extensions (e.g., .txt,.md):")
    if extensions:
        return [ext.strip().lower() for ext in extensions.split(',')]
    return []

def get_save_location(default_name):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".md",
        initialfile=f"{default_name}.md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
        title="Save Output As"
    )
    return file_path

def build_tree_structure(files):
    tree = {}
    for file_path in files:
        parts = file_path.split(os.sep)
        current_level = tree
        for part in parts[:-1]:  # folders
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
        current_level[parts[-1]] = None  # mark as a file
    return tree

def print_tree(tree, prefix=""):
    output = ""
    entries = list(tree.keys())
    for i, name in enumerate(entries):
        is_last = (i == len(entries) - 1)
        new_prefix = "    " + prefix
        if prefix.endswith("├── "):
            new_prefix = prefix.replace("├── ", "│   ") + ("    " if is_last else "│   ")
        elif prefix.endswith("└── "):
            new_prefix = prefix.replace("└── ", "    ") + ("    " if is_last else "│   ")

        if tree[name] is None:  # It's a file
            output += f"{prefix}├── {name}\n"
        else:  # It's a folder
            output += f"{prefix}├── {name}\n"
            output += print_tree(tree[name], new_prefix)
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
        result += f"\n## {file}\n\n"
        result += "```\n"
        result += content
        result += "\n```\n"
    return result

def main():
    directory = get_directory_path()
    if not directory:
        print("No directory selected.")
        return

    extensions = get_extensions()
    if not extensions:
        print("No extensions provided.")
        return

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

    # Ask where to save with suggested filename
    save_path = get_save_location(root_name)
    if save_path:
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"File saved successfully to: {save_path}")
        except Exception as e:
            print(f"Failed to save file: {e}")
    else:
        print("Save operation canceled.")

if __name__ == "__main__":
    main()