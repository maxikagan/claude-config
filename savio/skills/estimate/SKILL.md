---
name: estimate
description: Estimate memory and partition for a SLURM job
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# SLURM Job Estimation

Analyze a job description and recommend SLURM settings.

## Usage

```
/estimate <job-description>
```

## Analysis Steps

1. **Identify data files**: If specific files/paths are mentioned, check their sizes with `ls -lh` or `du -sh`.

2. **Estimate memory requirements** using these heuristics:
   - Parquet file size × 3-5 = loaded memory
   - CSV file size × 2-3 = loaded memory
   - Pandas operations can temporarily 2-3× memory
   - Joins/merges: (size of both dataframes) × 2-3
   - String operations on large columns: can 2× memory
   - Add 20% safety buffer

3. **Recommend partition**:
   | Partition | RAM | Use When |
   |-----------|-----|----------|
   | `savio2` | ~64 GB | Est. memory < 50 GB, simple jobs |
   | `savio3` | ~95 GB | Est. memory 50-80 GB, most jobs |
   | `savio3_bigmem` | ~386 GB | Est. memory > 80 GB, large states (CA/TX/FL/NY), big joins |

4. **Recommend time**: Based on data size and operation complexity.

5. **Recommend cpus-per-task**:
   - I/O bound (reading files): 4-8 cores
   - CPU bound (computation): 16-32 cores
   - Memory bound (large data): fewer cores to leave RAM headroom

## Output

Provide a ready-to-use SLURM header block:

```bash
#SBATCH --partition=<recommended>
#SBATCH --cpus-per-task=<recommended>
#SBATCH --time=<recommended>
# Estimated peak memory: <X> GB
# Reasoning: <brief explanation>
```
