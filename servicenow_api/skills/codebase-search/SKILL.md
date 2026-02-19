---
name: systems-manager-codebase-search
description: Fast and precise codebase search using ripgrep (rg) and glob patterns.
---
# Codebase Search Skill

This skill provides powerful capabilities for searching codebases using `ripgrep` (rg) and glob patterns. These tools are the foundation for efficient agentic exploration.

## Tools

### 1. ripgrep (rg)
- **Description**: A line-oriented search tool that recursively searches directories for a regex pattern.
- **Why use it**: It's faster than standard grep, respects `.gitignore`, and provides cleaner output for LLMs.
- **Common Flags**:
    - `-n`: Show line numbers (essential for context).
    - `-i`: Case insensitive search.
    - `-C 2`: Show 2 lines of context around matches.
    - `-t <type>`: Filter by file type (e.g., `-t py`, `-t js`).
    - `-g <glob>`: Include/exclude files based on glob patterns.
- **Example Usage**:
    ```bash
    rg "class User" -t py -n
    rg "TODO" -g "!tests/" -C 2
    ```

### 2. Glob
- **Description**: Pattern matching for file paths.
- **Usage**: Use with `rg`, `find`, or directly via shell.
- **Patterns**:
    - `*`: Matches any characters in a filename.
    - `**`: Matches directories recursively.
    - `?`: Matches a single character.
    - `[...]`: Matches a range of characters.
- **Example**:
    ```bash
    ls **/*.py
    rg --files -g "**/*.{js,ts}"
    ```

## Agentic Workflow
1.  **Global Discovery**: Start with `ls -R` or `fd` to map the structure.
2.  **Narrow Search**: Use `glob` patterns to filter relevant files.
3.  **Precise Search**: Use `rg` to find specific symbols or text within the narrowed set.
4.  **Read**: Finally, read the content of the identified files.

## Best Practices
- **Prefer `rg` over `grep`**: Always use `ripgrep` for code searches due to its speed and ignore-handling.
- **Use Context**: When searching for code, always request context lines (`-C`) to understand usage.
- **Filter**: Use file type filters (`-t`) to reduce noise.
