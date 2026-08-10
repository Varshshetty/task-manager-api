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
            "GET /tasks": "List all tasks (supports ?status= and ?priority= filters)",
            "GET /tasks/<id>": "Get one task",
            "POST /tasks": "Create a task",
            "PUT /tasks/<id>": "Update a task",
            "DELETE /tasks/<id>": "Delete a task",
        },
    })


@app.route("/tasks", methods=["GET"])
def get_tasks():
    """Return tasks, optionally filtered by ?status= and/or ?priority= query params."""
    query = Task.query

    status = request.args.get("status")
    priority = request.args.get("priority")

    if status:
        if status not in VALID_STATUSES:
            return jsonify({"error": f"status must be one of {sorted(VALID_STATUSES)}"}), 400
        query = query.filter_by(status=status)

    if priority:
        if priority not in VALID_PRIORITIES:
            return jsonify({"error": f"priority must be one of {sorted(VALID_PRIORITIES)}"}), 400
        query = query.filter_by(priority=priority)

    tasks = query.all()
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


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update one or more fields on an existing task."""
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": f"No task found with id {task_id}"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON with at least one field to update."}), 400

    if "title" in data:
        if not str(data["title"]).strip():
            return jsonify({"error": "title cannot be empty."}), 400
        task.title = data["title"].strip()

    if "description" in data:
        task.description = data["description"].strip() if data["description"] else None

    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"status must be one of {sorted(VALID_STATUSES)}"}), 400
        task.status = data["status"]

    if "priority" in data:
        if data["priority"] not in VALID_PRIORITIES:
            return jsonify({"error": f"priority must be one of {sorted(VALID_PRIORITIES)}"}), 400
        task.priority = data["priority"]

    db.session.commit()
    return jsonify(task.to_dict())


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by its id."""
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": f"No task found with id {task_id}"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": f"Task {task_id} deleted."}), 200


if __name__ == "__main__":
    app.run(debug=True)