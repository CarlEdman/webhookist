# CLAUDE.md — Webhookist Codebase Guide

## Project Overview

**Webhookist** is a learning project for exploring FastAPI and related Python web development packages. It implements a simple webhook management API with WebSocket support for real-time messaging.

- **Language:** Python 3.13+
- **Framework:** FastAPI (ASGI)
- **Package Manager:** UV (Astral)
- **Server:** Uvicorn

---

## Directory Structure

```
webhookist/
├── CLAUDE.md              # This file
├── README.md              # Minimal project description
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependency graph (do not edit manually)
├── Dockerfile             # Docker container definition
├── .python-version        # Pins Python 3.13
├── .gitignore
├── .dockerignore
├── src/                   # All application source code
│   ├── server.py          # FastAPI app entry point; all routes
│   ├── models.py          # SQLModel database models
│   ├── settings.py        # Pydantic-based configuration (env vars)
│   ├── security.py        # Authentication, password hashing, token dep
│   ├── websockets.py      # WebSocket connection management
│   ├── templates.py       # Jinja2 template configuration
│   ├── static.py          # Static files mount
│   ├── log.py             # Rich-based logger setup
│   ├── cli.py             # Typer CLI commands (demo only)
│   └── __init__.py        # Re-exports main components
└── static/                # Static assets served at /static
    ├── index.html          # WebSocket chat UI
    ├── favicon.ico
    ├── icon.jpeg
    └── styles.css          # Placeholder (currently empty)
```

---

## Running the Application

### Local development

```bash
# Install dependencies (uses uv.lock for reproducibility)
uv sync

# Run the server
uv run src/server.py
# Starts on http://127.0.0.1:80 by default
```

### Docker

```bash
docker build -t webhookist .
docker run -p 7777:7777 webhookist
# Listens on 0.0.0.0:7777 inside the container
```

---

## Configuration

Configuration lives in `src/settings.py` using `pydantic-settings`. All settings are read from environment variables prefixed with `FPT_`, or from a `.env` file in the project root.

| Env Var        | Default                  | Description                        |
|----------------|--------------------------|------------------------------------|
| `FPT_HOST`     | `127.0.0.1`              | Host address for Uvicorn           |
| `FPT_PORT`     | `80`                     | Port for Uvicorn                   |
| `FPT_SQLURL`   | `sqlite:///database.db`  | SQLAlchemy connection string       |
| `FPT_SALT`     | `webhookist`             | Application salt for crypto        |

**Docker defaults:** `FPT_HOST=0.0.0.0`, `FPT_PORT=7777`.

**PostgreSQL example:**
```
FPT_SQLURL=postgresql://user:password@host:5432/dbname
```

---

## Source File Reference

### `src/server.py` — Application entry point
- Creates the `FastAPI` app with a `lifespan` context manager.
- On startup: creates all DB tables and seeds a default `superuser` account (id=0) if absent.
- Mounts `/static` and the WebSocket endpoint `/ws`.
- Adds `HTTPSRedirectMiddleware` (redirects HTTP → HTTPS).
- Defines all HTTP routes (see API Routes below).
- Runs Uvicorn when executed directly (`python src/server.py`).

**Key dependency types defined here:**
- `SessionDep` — injects a SQLModel `Session`
- `UserDep` — injects the authenticated `User` via OAuth2 token

### `src/models.py` — Database models
- `User` — Non-table base model (id, username, disabled, superuser).
- `UserInDB` — Extends `User`, maps to the `users` table; adds `password_hash`.
- `Hook` — Maps to the `hooks` table; fields: id, user_id, name, content (max 64KB).

### `src/settings.py` — Configuration
- Single `Settings` instance exported as `settings`.
- Import: `from settings import settings`.

### `src/security.py` — Authentication
- `hash_password(password)` — Hashes with Argon2 + SASLprep normalization.
- `test_password(password, hash)` — Verifies a password against a hash.
- `get_current_user(token)` — FastAPI dependency; decodes token and returns `User`; raises 401/403 on failure.
- `TokenDep` — `Annotated` type alias for injecting the OAuth2 Bearer token string.
- `security_scheme` — `OAuth2PasswordBearer` pointing at `tokenUrl="token"`.

### `src/websockets.py` — WebSocket handling
- Maintains a module-level `set[WebSocket]` of active connections.
- `broadcast(msg)` — Sends `msg` to all connected clients concurrently using `asyncio.TaskGroup`.
- `endpoint(websocket)` — WebSocket handler; accepts connections, echoes received text to all clients, handles disconnect/errors.

### `src/log.py` — Logging
- Exports `log` — a standard `logging.Logger` using `RichHandler` for colored output.
- Import: `from log import log`.

### `src/cli.py` — CLI (demo)
- Typer app with two commands: `hello <name>` and `goodbye <name> [--formal]`.
- Run: `uv run src/cli.py hello world`.

---

## API Routes

| Method   | Path               | Auth | Description                           |
|----------|--------------------|------|---------------------------------------|
| GET      | `/`                | No   | Serves `static/index.html`            |
| GET      | `/favicon.ico`     | No   | Serves favicon                        |
| GET      | `/users/me`        | Yes  | Returns current authenticated user   |
| GET      | `/users/`          | Yes  | **Broken** — references undefined `token` |
| GET      | `/users/{user_id}` | Yes  | **Stub** — returns hook_id JSON       |
| GET      | `/hooks/`          | Yes  | **Broken** — references undefined `token` |
| GET      | `/hooks/{hook_id}` | Yes  | Returns hook_id as JSON               |
| POST     | `/hooks`           | Yes  | **Unimplemented** (`pass`)            |
| DELETE   | `/hooks/{hook_id}` | Yes  | **Unimplemented** (`pass`)            |
| PATCH    | `/hooks/{hook_id}` | Yes  | **Unimplemented** (`pass`)            |
| WS       | `/ws`              | No   | WebSocket chat broadcast endpoint     |

**Auth:** Routes marked "Yes" require an `Authorization: Bearer <token>` header via `UserDep`.

---

## Known Issues (as of current state)

These are pre-existing bugs in the codebase — do not introduce workarounds without fixing the root cause:

1. **`/users/` and `/hooks/` routes** reference an undefined variable `token` (line 65, 77 in server.py). These routes will raise a `NameError` at runtime.
2. **`/users/{user_id}` route** declares parameter `hook_id` but the path uses `user_id`; parameter name mismatch.
3. **`decode_token` is undefined** in `security.py` — `get_current_user` calls it but it is never defined, so all authenticated routes raise `NameError`.
4. **Hardcoded superuser password** (`"ragamuffin"`) in `server.py:38` — should use `secrets.token_urlsafe()` (commented out) before any production or shared use.
5. **Duplicate `User` import** in `src/__init__.py` — `User` is imported from both `models` and `security` (which re-imports it), causing a name collision.
6. **Missing `templates/` directory** — `src/templates.py` configures Jinja2 templates but no templates directory exists; any template rendering will fail.
7. **`PATCH /hooks/{hook_id}`** does not exist semantically — the route is registered but the handler is `pass`.

---

## Dependencies

Managed via `pyproject.toml` and locked in `uv.lock`. Use `uv sync` to install.

| Package              | Purpose                                      |
|----------------------|----------------------------------------------|
| `fastapi[standard]`  | Web framework + standard extras (httpx, etc.)|
| `uvicorn`            | ASGI server                                  |
| `sqlmodel`           | ORM combining SQLAlchemy + Pydantic          |
| `pydantic`           | Data validation                              |
| `pydantic-settings`  | Settings management from env/`.env`          |
| `jinja2`             | HTML template engine                         |
| `passlib`            | Password hashing (Argon2 backend via pwdlib) |
| `pwdlib[argon2]`     | Modern Argon2 password hashing               |
| `pyjwt`              | JWT token encode/decode                      |
| `pyopenssl`          | SSL/TLS support                              |
| `python-multipart`   | Form data parsing (required for OAuth2 form) |
| `redis[hiredis]`     | Redis client (installed, not yet wired in)   |
| `typer`              | CLI framework                                |
| `websocket`          | WebSocket protocol support                   |

**To add a dependency:**
```bash
uv add <package>
# This updates pyproject.toml and uv.lock
```

**Never edit `uv.lock` manually.**

---

## Code Conventions

- **Shebang line:** All executable `.py` files begin with `#! python3`.
- **Type hints:** Use modern Python 3.10+ union syntax (`X | Y`, not `Optional[X]`).
- **Annotated dependencies:** FastAPI dependencies are expressed as `Annotated[Type, Depends(...)]` type aliases (e.g., `SessionDep`, `UserDep`, `TokenDep`).
- **Imports:** Module-level relative-style imports (e.g., `from settings import settings`). Modules run from the `src/` directory as working directory.
- **Logging:** Use `from log import log` and call `log.info(...)`, `log.warning(...)`, etc.
- **No test framework** is configured. There are no tests. If adding tests, use `pytest` with `uv add --dev pytest`.

---

## Database

- Default: **SQLite** at `database.db` in the working directory.
- Switch to PostgreSQL by setting `FPT_SQLURL`.
- Schema is created on startup via `SQLModel.metadata.create_all(engine)`.
- Tables: `users`, `hooks`.
- The SQLite engine is created with `check_same_thread=False` and `echo=True` (SQL logged to stdout).

---

## Development Notes for AI Assistants

- All source files live under `src/`. Run commands from the project root with `uv run src/<file>.py`.
- The app imports modules by short name (e.g., `from settings import settings`), which works because Uvicorn/Python resolves relative to the `src/` directory when running `src/server.py` as `__main__`.
- Several routes and functions are **stubs or broken** (see Known Issues). When fixing them, prefer implementing the full intended behavior over patching around the bug.
- The `decode_token` function in `security.py` is the most critical missing piece — nothing requiring authentication will work until it is implemented (likely using `pyjwt`).
- Redis is installed but not integrated anywhere. It is likely intended for session storage or pub/sub for WebSocket broadcasting at scale.
- The `HTTPSRedirectMiddleware` means the local dev server will redirect all HTTP requests. During local development without TLS, either remove this middleware or use HTTPS.
