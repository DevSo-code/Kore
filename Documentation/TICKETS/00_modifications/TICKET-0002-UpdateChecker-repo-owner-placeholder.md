# TICKET-0002-UpdateChecker-repo-owner-placeholder (moved)


- **Area**: Core / Updates
- **Functionality**: In-app update checker
- **Status**: Open

## Why
`UpdateChecker` defaults to `repo_owner="yourusername"` and `repo_name="kore"`. Unless configured, it will not check the correct GitHub repository.

## Code references
- `src/ui/app.py`
  - `_check_for_updates()` instantiates `UpdateChecker()` with defaults
- `src/core/update_checker.py`
  - `__init__(self, repo_owner: str = "yourusername", repo_name: str = "kore")`

## Acceptance criteria
- Update checker queries the real upstream repo.
- If the configuration is missing, the checker fails safely and does not spam errors.

## Notes
Options:
- Add config/env var for repo owner/name.
- Or load from `constants.py`.

