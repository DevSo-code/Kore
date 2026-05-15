# SCHEMA.md — Database Schema (SQLite)

## Overview
Lightweight local SQLite database for settings persistence and download history. No authentication or multi-user support in MVP.

## Tables

### `settings`
Application configuration key-value store.

| Column | Type | Constraints |
|--------|------|-------------|
| `key` | TEXT | PRIMARY KEY |
| `value` | TEXT | NOT NULL |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

**Seed data**:
- `theme` → `"dark"`
- `default_output_dir` → `"/home/user/SwissPy"`
- `gpu_acceleration` → `"true"`
- `last_active_tab` → `"image"`

---

### `download_history`
Log of completed video downloads.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `url` | TEXT | NOT NULL |
| `title` | TEXT | |
| `format_id` | TEXT | NOT NULL |
| `resolution` | TEXT | |
| `file_path` | TEXT | NOT NULL |
| `file_size_bytes` | INTEGER | |
| `status` | TEXT | CHECK(status IN ('completed','failed','cancelled')) |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

---

### `processing_queue` (Future-proofing for Phase 2)
Tracks background image jobs.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `input_path` | TEXT | NOT NULL |
| `output_path` | TEXT | |
| `operation` | TEXT | CHECK(operation IN ('bg_removal')) |
| `status` | TEXT | CHECK(status IN ('pending','processing','done','error')) |
| `error_message` | TEXT | |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| `completed_at` | TIMESTAMP | |

## Access Pattern
- Use `sqlite3` stdlib with a small `Repository` class per table
- All writes happen on a background thread; reads are synchronous for settings
- WAL mode enabled for better concurrency