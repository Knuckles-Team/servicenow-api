# CRON.md - Persistent Scheduled Tasks
Last updated: 2026-02-21 02:20

## Active Tasks

| ID          | Name              | Interval (min) | Prompt                              | Last run          | Next approx |
|-------------|-------------------|----------------|-------------------------------------|-------------------|-------------|
| heartbeat   | Heartbeat         | 30             | @HEARTBEAT.md                       | —                 | —           |
| log-cleanup | Log Cleanup       | 720            | __internal:cleanup_cron_log         | —                 | —           |

*Edit this table to add/remove tasks. The agent reloads it periodically.*
*Use `@filename.md` in the Prompt column to load a multi-line prompt from a workspace file.*
