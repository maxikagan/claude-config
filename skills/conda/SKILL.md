---
name: conda
description: Conda Environment Activation
user-invocable: true
allowed-tools: Bash
---

# Conda Environment Activation

Activate a conda environment for the user. If no environment name is provided, list available environments.

## Usage

```
/conda [environment-name]
```

## Behavior

If an environment name is given as argument, activate it with:
```bash
conda activate <environment-name>
```

If no argument is provided, list available environments with:
```bash
conda env list
```
