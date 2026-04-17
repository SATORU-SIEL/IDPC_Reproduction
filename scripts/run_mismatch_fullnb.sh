#!/usr/bin/env bash
# Run the 4 mismatch full-notebook variants sequentially.
# Before each run, restore the original IDPC_Reproduction/ state from the
# backup; after each run, snapshot the fresh Chapter7/ outputs to
# backups/mm_fullnb_<pattern>/.
set -euo pipefail
cd "$(dirname "$0")/.."

source .venv/bin/activate

BACKUP_SRC="backups/mm_original_state"
mkdir -p backups

restore_original () {
  # restore chapter dirs
  for d in Chapter2 Chapter3 Chapter5 Chapter7 Figures; do
    rm -rf "IDPC_Reproduction/$d"
    cp -a "$BACKUP_SRC/$d" "IDPC_Reproduction/$d"
  done
  # restore flat CSVs that the pipeline overwrites
  for f in "$BACKUP_SRC"/*.csv; do
    cp -a "$f" "IDPC_Reproduction/$(basename "$f")"
  done
}

for pattern in derangement shift1 reverse random; do
  echo "================= $pattern ================="
  restore_original
  nb_in="IDPC_Reproduction_mmfull_${pattern}.ipynb"
  nb_out="IDPC_Reproduction_mmfull_${pattern}_executed.ipynb"
  echo "[nbconvert] $nb_in → $nb_out ..."
  time jupyter nbconvert --to notebook --execute --allow-errors \
    --output "$nb_out" "$nb_in"
  echo "[snapshot] Chapter7/ → backups/mm_fullnb_${pattern}/"
  rm -rf "backups/mm_fullnb_${pattern}"
  mkdir -p "backups/mm_fullnb_${pattern}"
  cp -a IDPC_Reproduction/Chapter7 "backups/mm_fullnb_${pattern}/"
  # also snapshot a couple of pooled CSVs that the pipeline rebuilds
  for f in J_dh_kappa_pooled_v2.csv \
           event_level_raw_table_TRUE_RICCI__HYBRID_PHI.csv \
           event_level_with_fes_phase_TRUE_RICCI.csv; do
    if [ -f "IDPC_Reproduction/$f" ]; then
      cp -a "IDPC_Reproduction/$f" "backups/mm_fullnb_${pattern}/$f"
    fi
  done
done

# final restore to leave IDPC_Reproduction/ pristine
echo "================= final restore ================="
restore_original
echo "done."
