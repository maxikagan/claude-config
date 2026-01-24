# Dewey Data Download

When downloading data from Dewey API on Savio HPC:

## Prerequisites
- API key stored in `/global/home/users/maxkagan/project_oakland/.env`
- uvx available at `~/.local/bin/uvx`

## SLURM Script Template
```bash
#!/bin/bash
#SBATCH --job-name=dewey_download
#SBATCH --account=fc_basicperms
#SBATCH --partition=savio2
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --time=08:00:00
#SBATCH --output=OUTPUT_DIR/download_%j.log
#SBATCH --error=OUTPUT_DIR/download_%j.err

OUTPUT_DIR="FILL_IN"
PROJECT_ID="FILL_IN"

source /global/home/users/maxkagan/project_oakland/.env

if [ -z "${DEWEY_API_KEY}" ]; then
    echo "ERROR: DEWEY_API_KEY environment variable not set"
    exit 1
fi

if [ ! -x ~/.local/bin/uvx ]; then
    echo "ERROR: uvx not found at ~/.local/bin/uvx"
    exit 1
fi

echo "Starting Dewey download at $(date)"
echo "Output directory: ${OUTPUT_DIR}"
echo "Project ID: ${PROJECT_ID}"

cd "${OUTPUT_DIR}" || { echo "ERROR: Failed to access ${OUTPUT_DIR}"; exit 1; }

~/.local/bin/uvx --from deweypy dewey \
    --api-key "${DEWEY_API_KEY}" \
    --download-directory "${OUTPUT_DIR}" \
    speedy-download "${PROJECT_ID}"

EXIT_CODE=$?

echo "Download completed at $(date) with exit code ${EXIT_CODE}"

if [ ${EXIT_CODE} -eq 0 ]; then
    echo "Listing downloaded files:"
    ls -lh "${OUTPUT_DIR}"
    echo "Total size:"
    du -sh "${OUTPUT_DIR}"
fi

exit ${EXIT_CODE}
```

## Key Points
1. **Source .env file** - Do NOT rely on `.bashrc` (non-interactive shell)
2. **Use full path to uvx** - `~/.local/bin/uvx`
3. **Specify --download-directory** - Avoids interactive prompt
4. **Specify --api-key** - Pass explicitly from env var
5. **Error checking** - Validate API key and uvx before download
6. **Wall time** - 8 hours for large datasets (176 GB ~= several hours)

## Workflow
1. Create output directory: `mkdir -p /global/scratch/users/maxkagan/PROJECT/DATASET_DATE/`
2. Copy template, fill in OUTPUT_DIR and PROJECT_ID
3. Submit: `sbatch script.sh`
4. Monitor: `squeue -j JOBID` and `tail -f OUTPUT_DIR/download_JOBID.log`
