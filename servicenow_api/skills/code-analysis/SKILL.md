---
name: systems-manager-code-analysis
description: Code Analysis using Tree-Sitter and Abstract Syntax Trees (AST).
---
# Code Analysis Skill

This skill provides capabilities for deep structural analysis of codebases using Tree-Sitter and ASTs. It enables agents to understand code structure, find definitions, and analyze dependencies beyond simple text search.

## Overview
Tree-sitter is a parser generator tool and an incremental parsing library. It builds a concrete syntax tree for a source file and efficiently updates the tree as the source file is edited.

## Capabilities

### 1. Structural Search (Tree-Sitter Query)
- **Goal**: Find code elements based on their syntactic structure (e.g., "all function definitions", "calls to function X", "assignments to variable Y").
- **Usage**: Use `python` to load `tree-sitter` and run queries.
- **Example**:
  ```python
  from tree_sitter import Language, Parser
  # Load language (requires building the language library first, or using python bindings)
  # For this environment, we recommend using pre-installed python bindings if available
  # or falling back to simple AST parsing for Python.
  ```

### 2. AST Traversal
- **Goal**: Walk the syntax tree to understand the hierarchy of code elements.
- **Usage**: Traverse nodes to find classes, methods, and their relationships.

### 3. Symbol Extraction
- **Goal**: Extract definitions of functions, classes, and variables with their locations.
- **Usage**: Useful for building a map of the codebase.

## Best Practices
- **Combine with Grep**: Use `ripgrep` to narrow down files, then use AST analysis for precision.
- **Handle Errors**: Tree-sitter is robust to syntax errors, but always check for missing nodes.
- **Language Support**: Ensure the appropriate language grammar is available.

## Tool Usage
Since `tree-sitter` CLI might not be installed, use Python scripts to leverage the library.

```python
import tree_sitter
# Implementation details specific to the environment
```
