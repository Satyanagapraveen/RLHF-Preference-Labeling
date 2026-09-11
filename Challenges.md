# Challenge 1: PostgreSQL container showed as unhealthy even though logs said it was ready

## Problem summary
When I ran `docker-compose up --build -d`, the app container built successfully, but the database container never became healthy enough for the app to start.

The output was:

```bash
Running 3/3
 ✔ rlhfpreferencelabeling-app              Built                                                                                                           0.0s 
 ✘ Container rlhfpreferencelabeling-db-1   Error                                                                                                           1.1s 
 ✔ Container rlhfpreferencelabeling-app-1  Recreated                                                                                                       0.6s 
dependency failed to start: container rlhfpreferencelabeling-db-1 is unhealthy
```

This was confusing because PostgreSQL logs showed it had started successfully.

---

## What actually happened
The database logs showed:

```bash
db-1  | PostgreSQL init process complete; ready for start up.
db-1  | 
db-1  | 2026-09-11 02:13:44.489 UTC [1] LOG:  starting PostgreSQL 15.15 (Debian 15.15-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
db-1  | 2026-09-11 02:13:44.491 UTC [1] LOG:  listening on IPv4 address "0.0.0.0", port 5432
db-1  | 2026-09-11 02:13:44.491 UTC [1] LOG:  listening on IPv6 address "::", port 5432
db-1  | 2026-09-11 02:13:44.504 UTC [1] LOG:  listening on Unix socket "/var/run/postgresql/.s.PGSQL.5432"
db-1  | 2026-09-11 02:13:44.522 UTC [64] LOG:  database system was shut down at 2026-09-11 02:13:44 UTC
db-1  | 2026-09-11 02:13:44.535 UTC [1] LOG:  database system is ready to accept connections
```

But Docker still reported the DB as unhealthy because the healthcheck itself was failing.

The healthcheck in Compose was:

```yaml
healthcheck:
  test: ["CMD", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
```

This is the root cause.

---

## Root cause
Docker health status is based on the result of the healthcheck command, not on the PostgreSQL log output.

The `CMD` form runs the command directly, without using a shell; it is not the safest way to run a readiness check for Postgres when environment variables and shell logic are involved.

This caused the health status to fail even though Postgres was actually ready.

There was also this line in the logs:

```bash
/usr/local/bin/docker-entrypoint.sh: ignoring /docker-entrypoint-initdb.d/*
```

This line means Docker ignored any SQL init scripts in `/docker-entrypoint-initdb.d`, but it was not the actual cause of the unhealthy status. The real issue was the healthcheck command syntax.

---

## Fix
I changed the healthcheck to use `CMD-SHELL`, which is the proper approach for a shell-based Postgres readiness check:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\" >/dev/null 2>&1 || exit 1"]
  interval: 5s
  timeout: 5s
  retries: 10
  start_period: 10s
```

This is safer because `CMD-SHELL` runs through the shell and allows proper variable expansion and exit handling.

---

## Why `CMD` and `CMD-SHELL` are different

### `CMD`
Runs the command directly, without a shell.

Example:

```yaml
["CMD", "pg_isready", "-U", "myuser", "-d", "mydb"]
```

This is effectively:

```bash
pg_isready -U myuser -d mydb
```

It does not handle shell features like `||`, `>`, or variable parsing in the same way.

### `CMD-SHELL`
Runs the command through the container shell, usually `sh -c`.

Example:

```yaml
["CMD-SHELL", "pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" >/dev/null 2>&1 || exit 1"]
```

This allows:
- shell logic such as `||`
- redirection like `>/dev/null 2>&1`
- proper handling of environment variables

---

## Key learning
The main lesson is:

- PostgreSQL logs saying “ready to accept connections” does NOT guarantee Docker marks the container healthy.
- Docker health status depends on the healthcheck command returning exit code `0`.
- For PostgreSQL, `CMD-SHELL` is the correct choice for a robust readiness check.

---

## Final note
When a container is marked unhealthy even though the app logs look fine, always check the container healthcheck command first. In this case, the failure was caused by the healthcheck syntax, not by PostgreSQL itself being down.

This issue was fixed by replacing:

```yaml
["CMD", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
```

with:

```yaml
["CMD-SHELL", "pg_isready -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\" >/dev/null 2>&1 || exit 1"]
```


