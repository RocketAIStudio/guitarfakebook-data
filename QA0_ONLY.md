# GuitarFakeBook QA-0 data branch

This branch contains exactly ten real, source-traceable GuitarFakeBook records for the bounded QA-0 gate.

- It is not the production corpus.
- It must not be merged or deployed until independent REVIEW passes.
- Source Guitar Pro binaries are not committed.
- The application must load `data/index.json` and `data/songs/{stable-id}.json` without a fixture fallback.
- The authoritative source trace and validation evidence are held in the application repository under `governance/light-build/gfb-lb02/`.

The full 13,493-song corpus is intentionally absent.
