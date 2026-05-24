# Design

## Confirmed Existing Implementation

- Backend file access is centralized in `apps/trellis-manager-desktop/app/file_reader.py`.
- API methods in `apps/trellis-manager-desktop/app/api.py` already expose:
  - `list_project_files(project_path, subroot)`
  - `read_project_file(project_path, relative_path)`
  - `read_project_jsonl(project_path, relative_path, limit, offset)`
  - `list_task_context_files(task_path)`
  - `read_task_context_file(task_path, filename, limit, offset)`
- Frontend components already exist:
  - `JsonlViewer` for collapsible JSONL rows and pagination.
  - `FileTreePanel` for file navigation.
  - `ProjectKnowledgeBrowser` for project-level spec/workspace browsing.
  - `TaskDetail` `Context` tab for task-level context browsing.

## Boundary

Keep the change frontend-only unless verification finds a backend bug. The missing behavior is visible breadcrumb text in preview panes; the backend already returns paths relative to `.trellis/`.

## UI Contract

- Context preview breadcrumb uses the selected item path, already relative to `.trellis/`.
- Task context file reads still pass the task-local path to `readTaskContextFile`.
- Knowledge browser breadcrumb uses `selected.path`.
- Breadcrumb is display-only; it must not introduce new path parsing or reads.

## Safety

Do not loosen SafeFileReader path checks. Existing tests cover traversal and symlink escape. The patch should not add new file-read surfaces.

## Rollback

Revert only the frontend breadcrumb additions if the UI change causes layout problems. Backend and API contracts should remain untouched.
