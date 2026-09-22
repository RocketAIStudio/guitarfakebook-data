# GuitarFakeBook V6.0 selected-artist wave R03

Status: STAGED_NOT_RELEASED. This is the approved 335-artist scope with the owner's feedback, preserved from the prior selected-artist package.

The selected artists have 2,237 catalog entries at application commit 0bf10064a8597ab1ea29bc0515815956fea50e0b. Six source-backed songs pass the existing automated checks, giving a projected 2,243 entries if released. Two existing artists gain songs: Bob Dylan 28 + 1 = 29; The Rolling Stones 44 + 5 = 49. Zero new artists are introduced by these six songs.

The original 2,002-source candidate queue contains 124 existing songs, 36 unavailable sources, 1,831 awaiting parsing/QA, five held and six qualified. It is not a 2,002-song gain.

## Files

- reports/GuitarFakeBook_V6.0_ARTISTS_CURRENT_VS_NEXT_WAVE_R03.csv: all 335 selected artist rows plus a total, with current, qualified additions, projected count and remaining dispositions.
- reports/GuitarFakeBook_V6.0_SONGS_CURRENT_VS_NEXT_WAVE_R03.csv: 2,237 current catalog rows and 2,002 candidate-source rows. A candidate that duplicates a current row is labeled SKIPPED_ALREADY_CURRENT; do not sum both row types as current catalog songs.
- songs/: six original qualified payloads, unchanged and SHA-256 verified.
- candidate-ledger.json and manifest.json: exact scope, disposition and source lineage.
- evidence/: original completed verification and dataset records, unchanged.

Current counts are catalog entries, including existing variants, and cover only the selected artist set. The app contains 13,025 total catalog entries. Current metadata was verified against the unchanged Git blob; no new live-site availability certification is claimed.

Staging does not change data/index.json, existing songs, the app or production. The active catalog gain remains zero. Independent review and song visual acceptance remain separately tracked; the current approval is recorded without inventing those results.

Continue the 1,831 pending sources using the pinned parser b8d9eb7078f3bfeb9cae61a972535bb119e9698c and existing source hashes. Preserve canonical production artist spelling, existing entries, net-new-only admission, English text, simple chords and successful transposition.
