from flask import Flask, request, jsonify, redirect, render_template
from todo_app.db import get_connection
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# @app.route("/")
# def health_check():
#     return "To-Do API is running."

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

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        app.logger.info(f"Task created successfully with id {task_id}")
        return jsonify({
            "id": task_id,
            "message": "Task created"
        }), 201
    
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
    

@app.route("/")
def show_tasks():
    conn = get_connection()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return render_template("tasks.html", tasks=tasks)

@app.route("/add", methods=["GET", "POST"])
def add_task_form():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        conn = get_connection()
        conn.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description)
        )
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add_task.html")

@app.route("/tasks/<int:task_id>/status", methods=["POST"])
def update_task_status(task_id):
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ?",
            ("done", task_id)
        )
        conn.commit()
        conn.close()
        return redirect("/")
    except Exception as e:
        app.logger.error(f"Error updating task status: {e}")
        return redirect("/")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task_ui(task_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return redirect("/")
    except Exception as e:
        app.logger.error(f"Error deleting task: {e}")
        return redirect("/")



if __name__ == "__main__":
    app.run(debug=True, port=8000)