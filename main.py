import os

def get_user_input(prompt):
    return input(prompt).strip()

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
    entries = list(tree.keys())
    for i, name in enumerate(entries):
        is_last = (i == len(entries) - 1)
        new_prefix = "    " + prefix
        if prefix.endswith("├── "):
            new_prefix = prefix.replace("├── ", "│   ") + ("    " if is_last else "│   ")
        elif prefix.endswith("└── "):
            new_prefix = prefix.replace("└── ", "    ") + ("    " if is_last else "│   ")

        if tree[name] is None:  # It's a file
            print(f"{prefix}├── {name}")
        else:  # It's a folder
            print(f"{prefix}├── {name}")
            print_tree(tree[name], new_prefix)

def generate_markdown_output(root, files):
    result = "\n---\n"
    for file in files:
        full_path = os.path.join(root, file)
        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        result += f"\n## {file}\n\n"
        result += "```\n"
        result += content
        result += "\n```\n"
    return result

def main():
    directory = get_user_input("Enter the directory path: ")
    while not os.path.isdir(directory):
        print("Invalid directory. Please try again.")
        directory = get_user_input("Enter the directory path: ")

    extensions_input = get_user_input("Enter comma-separated file extensions (e.g., .txt,.md): ")
    extensions = [ext.strip().lower() for ext in extensions_input.split(',')]

    matched_files = []

    for root_dir, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                rel_path = os.path.relpath(os.path.join(root_dir, file), directory)
                matched_files.append(rel_path)

    if not matched_files:
        print("No matching files found.")
        return

    print("\n# " + os.path.basename(os.path.abspath(directory)) + "\n")
    print(".")
    tree_structure = build_tree_structure(matched_files)
    print_tree(tree_structure)

    markdown_output = generate_markdown_output(directory, matched_files)
    print(markdown_output)

if __name__ == "__main__":
    main()