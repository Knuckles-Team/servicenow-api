---
name: systems-manager-file-navigation
description: Efficient file navigation and structure mapping.
---
# File Navigation Skill

This skill encompasses tools and strategies for navigating directory structures, understanding project layouts, and locating files.

## Tools

### 1. `tree`
- **Description**: Displays directories and files as a recursive tree.
- **Usage**: Good for a quick overview of project structure.
- **Flags**:
    - `-L <level>`: Limit recursion depth.
    - `-I <pattern>`: Ignore files matching pattern.
    - `-d`: List directories only.

### 2. `fd` a.k.a `fd-find`
- **Description**: A faster alternative to `find`.
- **Usage**: Quickly locate files by name.
- **Flags**:
    - `-H`: Include hidden files.
    - `-I`: Ignore `.gitignore`.
    - `-e <ext>`: Filter by file extension.

### 3. `ls` (standard)
- **Description**: List directory contents.
- **Usage**: Basic navigation.
- **Flags**:
    - `-R`: Recursive list.
    - `-a`: Show hidden files.
    - `-l`: Long format (permissions, size, etc.).

## Agentic Workflow
1.  **Assess Structure**: Use `tree -L 2` to understand the high-level layout.
2.  **Explore Details**: Use `ls -l` to inspect specific directories.
3.  **Locate**: Use `fd` (or `find`) to locate specific files or patterns (e.g., config files).
4.  **Map**: Build a mental map of where components (src, tests, docs) reside.

## Best Practices
- **Limit Depth**: Always use depth limits (`-L` or `-maxdepth`) when exploring large repos to avoid overwhelming output.
- **Ignore Noise**: Use `-I` or `.gitignore` to skip `node_modules`, `venv`, etc.
- **Combine**: Use `fd` to find files, then `xargs` to process them (e.g., `fd -e py | xargs wc -l`).
