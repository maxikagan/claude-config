---
globs: ["**/*.ts", "**/*.tsx"]
---

# TypeScript Rules

## Naming
- `PascalCase` for interfaces, types, classes, components
- `camelCase` for functions, variables, methods
- `SCREAMING_SNAKE_CASE` for constants
- `kebab-case` for file names

## Type Safety
- No `any` without documented reason
- No `@ts-ignore` without explanation
- Prefer `unknown` over `any` when type is uncertain
- Explicit return types on exported functions

## Imports
- Group: external → internal → relative
- Prefer named exports over default exports
- No circular dependencies

## Async Code
- Always handle promise rejections
- Use try/catch for async operations
- No floating promises
