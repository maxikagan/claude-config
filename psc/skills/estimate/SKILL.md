---
name: estimate
description: Estimate memory and partition for a SLURM job on PSC Bridges-2
user-invocable: true
allowed-tools: Bash, Read, Glob, Grep
---

# SLURM Job Estimation (PSC Bridges-2)

Analyze a job description and recommend SLURM settings for Bridges-2.

## Usage

```
/estimate <job-description>
```

## Analysis Steps

1. **Identify data files**: If specific files/paths are mentioned, check their sizes with `ls -lh` or `du -sh`.

2. **Estimate memory requirements** using these heuristics:
   - Parquet file size x 3-5 = loaded memory
   - CSV file size x 2-3 = loaded memory
   - Pandas operations can temporarily 2-3x memory
   - Joins/merges: (size of both dataframes) x 2-3
   - String operations on large columns: can 2x memory
   - Add 20% safety buffer

3. **Recommend partition** (prefer shared to save SUs):

   | Partition | RAM | Cores | SU Cost | Use When |
   |-----------|-----|-------|---------|----------|
   | `RM-shared` | 2GB/core (256GB max) | up to 64 | 1 SU/core/hr | Default choice. Est. memory < 128 GB |
   | `RM` | 256GB | 128 (full node) | 128 SU/hr | Need >64 cores or full node memory |
   | `RM-512` | 512GB | 128 (full node) | 128 SU/hr | Est. memory > 256 GB |
   | `GPU-shared` | varies | up to 4 GPUs | 1 SU/GPU/hr (v100/l40s), 2 SU (h100) | GPU workloads |
   | `GPU` | varies | up to 64 GPUs | 8 SU/hr per v100 node | Multi-node GPU |

4. **For RM-shared, calculate cores needed**:
   - Each core gets 2GB RAM on RM-shared
   - If you need 32GB RAM, request at least 16 cores (`--ntasks-per-node=16`)
   - I/O bound (reading files): 4-8 cores
   - CPU bound (computation): 16-32 cores
   - Memory bound (large data): calculate cores from RAM need (RAM_GB / 2)

5. **Recommend time**: Based on data size and operation complexity.

## Output

Provide a ready-to-use SLURM header block:

```bash
#SBATCH -N 1
#SBATCH -p <partition>
#SBATCH --ntasks-per-node=<cores>   # For RM-shared
#SBATCH --gpus=<type>:<count>       # For GPU-shared (omit for RM)
#SBATCH -t <time>
#SBATCH -A soc260001p
#SBATCH -o slurm-%j.out
# Estimated peak memory: <X> GB (requesting <Y> cores x 2GB = <Z> GB)
# Estimated SU cost: <N> SUs
# Reasoning: <brief explanation>
```

Always include the SU cost estimate so the user can make an informed decision.
