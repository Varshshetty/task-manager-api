# Task Manager API

A simple REST API for managing tasks, built with Flask and SQLAlchemy. Supports creating, listing, filtering, updating, and deleting tasks, plus a status-count summary endpoint.

## Tech stack

- Python 3
- Flask
- Flask-SQLAlchemy
- SQLite (file-based, no separate DB server needed)

## Setup

1. Clone the repo and move into it:
   ```bash
   git clone <your-repo-url>
   cd task-manager-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the server:
   ```bash
   python app.py
   ```

The API will be available at `http://127.0.0.1:5000`. A `tasks.db` SQLite file is created automatically on first run.

## Data model

Each task has:

| Field         | Type     | Notes                                              |
|---------------|----------|-----------------------------------------------------|
| `id`          | integer  | Auto-generated primary key                         |
| `title`       | string   | Required                                            |
| `description` | string   | Optional                                            |
| `status`      | string   | One of `todo`, `in-progress`, `done`. Defaults to `todo` |
| `priority`    | string   | One of `low`, `medium`, `high`. Defaults to `medium` |
| `created_at`  | datetime | Auto-set on creation, returned as ISO 8601          |

## Endpoints

### `GET /`
Welcome route with a list of available endpoints.

### `GET /tasks`
List all tasks. Supports optional query params:
- `?status=todo|in-progress|done`
- `?priority=low|medium|high`

Both can be combined, e.g. `GET /tasks?status=todo&priority=high`.

**Example response**
```json
[
  {
    "id": 1,
    "title": "Write README",
    "description": null,
    "status": "todo",
    "priority": "high",
    "created_at": "2026-08-21T10:15:00"
  }
]
```

### `GET /tasks/<id>`
Return a single task by id. `404` if it doesn't exist.

### `GET /tasks/count`
Return the total number of tasks and a breakdown per status.

**Example response**
```json
{
  "total": 7,
  "by_status": {
    "done": 2,
    "in-progress": 1,
    "todo": 4
  }
}
```

### `POST /tasks`
Create a new task. `title` is required; everything else is optional.

**Example request body**
```json
{
  "title": "Deploy to production",
  "description": "Push final build and verify",
  "status": "todo",
  "priority": "high"
}
```

Returns the created task with a `201` status code.

### `PUT /tasks/<id>`
Update one or more fields on an existing task. Only send the fields you want to change.

**Example request body**
```json
{
  "status": "done"
}
```

### `DELETE /tasks/<id>`
Delete a task by id. Returns a confirmation message with `200`, or `404` if the task doesn't exist.

## Error handling

Invalid `status` or `priority` values return a `400` with a message listing the accepted values. Requests for a task id that doesn't exist return a `404`.

## Example usage (curl)

```bash
# Create a task
curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn Flask", "priority": "high"}'

# List all in-progress tasks
curl http://127.0.0.1:5000/tasks?status=in-progress

# Get task counts by status
curl http://127.0.0.1:5000/tasks/count

# Mark a task done
curl -X PUT http://127.0.0.1:5000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'

# Delete a task
curl -X DELETE http://127.0.0.1:5000/tasks/1
```

## Notes

This is a development server (`debug=True`) and not intended for production use as-is. For production, run behind a WSGI server such as Gunicorn.
