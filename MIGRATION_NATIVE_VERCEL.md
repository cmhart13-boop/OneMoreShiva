# Shiva native Vercel migration

This repository is being migrated from the legacy Streamlit runtime to a native Next.js application.

Acceptance gate before production cutover:
- zero Streamlit imports, packages, entrypoints, runtime assets, or DOM selectors in the production tree
- mobile-first fixed bottom navigation rendered against the physical viewport
- Home, Draft, Guide, and Coach all functional
- ESPN sync, league selection, My Team, rankings, mock-draft logic, queue, historical data, and session behavior preserved or reimplemented in native code
- production build and runtime logs clean
- mobile render verified before production alias is moved

The legacy app must remain isolated from the native production bundle during migration.
