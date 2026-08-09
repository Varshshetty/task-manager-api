from flask import Flask, request, jsonify
from models import db, Task

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db.init_app(app)

VALID_STATUSES = {"todo", "in-progress", "done"}
VALID_PRIORITIES = {"low", "medium", "high"}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    """A simple welcome route so visiting the root URL isn't a 404."""
    return jsonify({
        "message": "Task Manager API is running.",
        "endpoints": {
            "GET /tasks": "List all tasks",
            "GET /tasks/<id>": "Get one task",
            "POST /tasks": "Create a task",
        },
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Return every task in the database."""
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Return a single task by its id, or a 404 if it doesn't exist."""
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": f"No task found with id {task_id}"}), 404
    return jsonify(task.to_dict())


@app.route("/tasks", methods=["POST"])
def create_task():
    """Create a new task from JSON in the request body."""
    data = request.get_json(silent=True)

    if not data or "title" not in data or not str(data["title"]).strip():
        return jsonify({"error": "A 'title' field is required."}), 400

    status = data.get("status", "todo")
    priority = data.get("priority", "medium")

    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {sorted(VALID_STATUSES)}"}), 400
    if priority not in VALID_PRIORITIES:
        return jsonify({"error": f"priority must be one of {sorted(VALID_PRIORITIES)}"}), 400

    task = Task(
        title=data["title"].strip(),
        description=data.get("description", "").strip() if data.get("description") else None,
        status=status,
        priority=priority,
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201


# NOTE: PUT (update) and DELETE endpoints, plus filtering by status/priority,
# will be added tomorrow.


if __name__ == "__main__":
    app.run(debug=True)
