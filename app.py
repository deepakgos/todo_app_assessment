from flask import Flask, request, jsonify
from db import get_connection
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def health_check():
    return "To-Do API is running."

# Create Task
@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        data = request.get_json()

        if not data or "title" not in data:
            return jsonify({"error": "Task title is required"}), 400
        
        conn = get_connection()
        conn.execute(
            """
                Insert into tasks (title, description, due_date, status)
                values (?, ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description"),
                data.get("due_date"),
                data.get("status", "pending")
            )
        )

        conn.commit()
        conn.close()

        app.logger.info("Task created successfully")
        return jsonify({"message": "Task created"}), 201
    
    except Exception as e:
        app.logger.error(f"Error creating task: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Get All Tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_connection()
        tasks = conn.execute("select * from tasks").fetchall()
        conn.close()

        result = [dict(task) for task in tasks]

        return jsonify(result), 200
    
    except Exception as e:
        app.logger.error(f"Error fetching tasks: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Get Single Task
@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        conn = get_connection()
        task = conn.execute(
            "Select * from tasks where id = ?", (task_id,)
        ).fetchone()
        conn.close()

        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify(dict(task)), 200
    except Exception as e:
        app.logger.error(f"Error fetching task: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Update Task  
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error":"No data provided"}), 400
        
        status = data.get("status", None)
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
                status,
                task_id
            )
        )

        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify({"message": "Task updated"}), 200
    
    except Exception as e:
        app.logger.error(f"Error updating task: {e}")
        return jsonify({"error": "Internal server error"}), 500


# Delete Task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        conn = get_connection()
        cursor = conn.execute(
            "Delete from tasks where id = ?", (task_id,)
        )
        conn.commit()
        conn.close()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted"}), 200
    
    except Exception as e:
        app.logger.error(f"Error deleting task: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)