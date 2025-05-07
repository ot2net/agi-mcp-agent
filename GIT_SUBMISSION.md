# Git Submission Guidelines

This document outlines the best practices for submitting code to the AGI-MCP-Agent repository.

## Commit Message Format

Please follow these guidelines for commit messages:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding or modifying tests
- **chore**: Changes to the build process or auxiliary tools

### Scope
The scope is optional and can be anything specifying the place of the commit change, such as:
- **mcp**: Changes to the Master Control Program
- **agent**: Changes to the agent framework
- **env**: Changes to the environment interfaces
- **api**: Changes to the API
- **ui**: Changes to the UI/frontend

### Subject
The subject contains a succinct description of the change:
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No period (.) at the end

### Body
The body should include the motivation for the change and contrast this with previous behavior.

### Footer
The footer should contain any information about Breaking Changes and reference GitHub issues that this commit closes.

## Branch Naming Convention

- **feature/**: For new features (e.g., feature/add-llm-agent)
- **fix/**: For bug fixes (e.g., fix/memory-leak)
- **docs/**: For documentation (e.g., docs/update-readme)
- **refactor/**: For refactoring (e.g., refactor/optimize-task-scheduler)
- **test/**: For test additions or modifications (e.g., test/agent-memory)

## Pull Request Process

1. Update the README.md and documentation with details of changes if applicable
2. Update the version numbers in any examples files and the README.md to the new version
3. The PR requires at least one review from a team member
4. You may merge the PR once you have the sign-off of at least one reviewer

## Required Files for Submission

When submitting your code, make sure to include:

1. All source code files (.py, .tsx, etc.)
2. Updated documentation if applicable
3. New or modified tests
4. Any configuration changes needed
5. Do NOT include:
   - .env files with sensitive information
   - poetry.lock (this is generated per environment)
   - __pycache__ directories, .pyc files
   - node_modules
   - Personal IDE configuration files 