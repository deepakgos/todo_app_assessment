from flask import Flask, request, jsonify, redirect, render_template
from todo_app.db import get_connection
import logging
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

API_BASE_URL = "http://127.0.0.1:8000"

# =========================
# API ROUTES (DB ACCESS)
# =========================

# Create Task
@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        data = request.get_json()

        if not data or "title" not in data:
            return jsonify({"error": "Task title is required"}), 400

        conn = get_connection()
        cursor = conn.execute(
            """
            INSERT INTO tasks (title, description, due_date, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description"),
                data.get("due_date"),
                data.get("status", "pending"),
            ),
        )

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        app.logger.info(f"Task created with id {task_id}")
        return jsonify({"id": task_id, "message": "Task created"}), 201

    except Exception as e:
        app.logger.error(f"Create task error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Get All Tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_connection()
        tasks = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()

        return jsonify([dict(task) for task in tasks]), 200

    except Exception as e:
        app.logger.error(f"Fetch tasks error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Get Single Task
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        conn = get_connection()
        task = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        conn.close()

        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify(dict(task)), 200

    except Exception as e:
        app.logger.error(f"Fetch task error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Update Task
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        conn = get_connection()
        cursor = conn.execute(
            """
            UPDATE tasks
            SET
                title = COALESCE(?, title),
                description = COALESCE(?, description),
                due_date = COALESCE(?, due_date),
                status = COALESCE(?, status)
            WHERE id = ?
            """,
            (
                data.get("title"),
                data.get("description"),
                data.get("due_date"),
                data.get("status"),
                task_id,
            ),
        )

        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task updated"}), 200

    except Exception as e:
        app.logger.error(f"Update task error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Delete Task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_connection()
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?", (task_id,)
        )
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted"}), 200

    except Exception as e:
        app.logger.error(f"Delete task error: {e}")
        return jsonify({"error": "Internal server error"}), 500


# =========================
# UI ROUTES (API CONSUMER)
# =========================

@app.route("/")
def show_tasks():
    response = requests.get(f"{API_BASE_URL}/api/tasks")
    tasks = response.json() if response.status_code == 200 else []
    return render_template("tasks.html", tasks=tasks)


@app.route("/add", methods=["GET", "POST"])
def add_task_form():
    if request.method == "POST":
        requests.post(
            f"{API_BASE_URL}/api/tasks",
            json={
                "title": request.form["title"],
                "description": request.form.get("description"),
                "due_date": request.form.get("due_date"),
            },
        )
        return redirect("/")

    return render_template("add_task.html")


@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_task_status(task_id):
    requests.put(
        f"{API_BASE_URL}/api/tasks/{task_id}",
        json={"status": "done"},
    )
    return redirect("/")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task_ui(task_id):
    requests.delete(f"{API_BASE_URL}/api/tasks/{task_id}")
    return redirect("/")


# =========================
# APP START
# =========================

if __name__ == "__main__":
    app.run(debug=True, port=8000)
