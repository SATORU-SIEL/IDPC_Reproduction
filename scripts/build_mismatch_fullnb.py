"""
Build four modified copies of the full IDPC_Reproduction.ipynb that
implement the prompt's 'skip SECTION 1.1-1.3 and real pairing, keep fake
pairing' protocol, with four different fake-pairing permutations:

  derangement   : original cell-7 logic with SEED=0 (random derangement)
  shift1        : σ(i) = (i+1) mod n
  reverse       : σ(i) = n-1-i
  random        : random derangement with SEED=42

Each output notebook IDPC_Reproduction_mmfull_<pattern>.ipynb:
  - Cells 2 (SECTION 1.1), 4 (SECTION 1.2), 5 (SECTION 1.3),
    and 8 (SECTION 1.4 real pairing) have cell_type set to "raw" → skipped.
  - Cell 7 (SECTION 1.4 ALTERNATIVE fake pairing) has its derangement
    generator replaced with the pattern-specific permutation.
  - All other cells are unchanged.
"""
from __future__ import annotations

import json
import os

SRC = "IDPC_Reproduction.ipynb"
PATTERNS = ["derangement", "shift1", "reverse", "random"]

SKIP_INDICES = [2, 4, 5, 8]     # 0-indexed cells to skip (SECTION 1.1, 1.2, 1.3, 1.4 real)
MISMATCH_CELL = 7               # 0-indexed cell 7 = SECTION 1.4 ALTERNATIVE

# the block we will swap out
DER_BLOCK_OLD = (
    "# Generate derangement (no true pairing)\n"
    "# ----------------------------\n"
    "perm = sessions.copy()\n"
    "found = False\n\n"
    "for trial in range(MAX_DERANGEMENT_TRIALS):\n"
    "    rng.shuffle(perm)\n"
    "    if all(p != s for p, s in zip(perm, sessions)):\n"
    "        found = True\n"
    "        break\n\n"
    "if not found:\n"
    "    raise RuntimeError(\n"
    "        f\"Failed to generate a derangement within {MAX_DERANGEMENT_TRIALS} trials.\"\n"
    "    )\n\n"
    "fake_map = {sessions[i]: perm[i] for i in range(len(sessions))}"
)


def new_block(pattern: str) -> str:
    if pattern == "derangement":
        return DER_BLOCK_OLD   # unchanged (default)
    if pattern == "shift1":
        return (
            "# shift+1 permutation — σ(i) = (i+1) mod n\n"
            "n = len(sessions)\n"
            "perm = [sessions[(i + 1) % n] for i in range(n)]\n"
            "found = True\n"
            "trial = 0\n"
            "fake_map = {sessions[i]: perm[i] for i in range(n)}"
        )
    if pattern == "reverse":
        return (
            "# reverse permutation — σ(i) = n-1-i\n"
            "n = len(sessions)\n"
            "perm = [sessions[n - 1 - i] for i in range(n)]\n"
            "found = True\n"
            "trial = 0\n"
            "fake_map = {sessions[i]: perm[i] for i in range(n)}"
        )
    if pattern == "random":
        return (
            "# random derangement — SEED=42 override\n"
            "rng = np.random.default_rng(42)\n"
            "perm = sessions.copy()\n"
            "found = False\n"
            "for trial in range(MAX_DERANGEMENT_TRIALS):\n"
            "    rng.shuffle(perm)\n"
            "    if all(p != s for p, s in zip(perm, sessions)):\n"
            "        found = True\n"
            "        break\n"
            "if not found:\n"
            "    raise RuntimeError('derangement not found')\n"
            "fake_map = {sessions[i]: perm[i] for i in range(len(sessions))}"
        )
    raise KeyError(pattern)


def main():
    for pattern in PATTERNS:
        nb = json.load(open(SRC))
        # skip cells
        for idx in SKIP_INDICES:
            nb["cells"][idx]["cell_type"] = "raw"
            # raw cells ignore outputs / execution_count
            nb["cells"][idx].pop("outputs", None)
            nb["cells"][idx].pop("execution_count", None)
        # mutate cell 7
        c7 = nb["cells"][MISMATCH_CELL]
        src = "".join(c7["source"])
        if DER_BLOCK_OLD not in src:
            raise RuntimeError("derangement block not found verbatim in cell 7")
        new_src = src.replace(DER_BLOCK_OLD, new_block(pattern))
        c7["source"] = new_src.splitlines(keepends=True)
        c7["outputs"] = []
        c7["execution_count"] = None
        # reset outputs on all cells for a clean run
        for c in nb["cells"]:
            if c.get("cell_type") == "code":
                c["outputs"] = []
                c["execution_count"] = None
        out = f"IDPC_Reproduction_mmfull_{pattern}.ipynb"
        json.dump(nb, open(out, "w"), indent=1)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
