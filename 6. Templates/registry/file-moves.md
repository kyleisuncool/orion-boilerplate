# File moves — the ledger

**Append-only.** Every file-plane move is a row, written by `.agents/scripts/fpmove.py` in the same step as the move, so the ledger never falls behind the disk. `repoint.py` reads it to fix vault pointers to moved files. Never edit a past row.

| Date | Old path | New path | Reason | Note |
|---|---|---|---|---|
