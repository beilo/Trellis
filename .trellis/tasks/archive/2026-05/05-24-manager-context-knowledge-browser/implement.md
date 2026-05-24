# Implementation Plan

1. Load relevant Manager files and confirm existing behavior.
   - Verify by reading backend API, SafeFileReader, task detail, project knowledge browser, JSONL viewer, and file tree components.

2. Add visible breadcrumb text to preview panes.
   - `TaskDetail` `TaskContextPane`: show selected `.trellis/<path>` above JSONL/Markdown preview.
   - `ProjectKnowledgeBrowser`: show selected `.trellis/<path>` above JSONL/Markdown preview.

3. Validate backend safety and frontend build.
   - `python3 apps/trellis-manager-desktop/tests/test_file_reader.py`
   - `pnpm --dir apps/trellis-manager-desktop/frontend build`

4. Run Trellis finish flow.
   - Review whether spec/changelog updates are needed.
   - Commit only files related to this issue; exclude pre-existing `.pyc` changes.
   - Archive the Trellis task and record the session.
