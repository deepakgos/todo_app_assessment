from flask import Flask, request, jsonify
from db import get_connection
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def health_check():
    return "To-Do API is running."

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


if __name__ == "__main__":
    app.run(debug=True, port=8000)