from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    "host": "localhost",
   "user": "talha",
   "password": "password",
    "database": "research_portal"
}

REQUIRED_FIELDS = ["title", "description", "research_area", "faculty_name",
                   "department", "required_skills", "available_positions",
                   "application_deadline"]


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    missing = [field for field in REQUIRED_FIELDS if not data.get(field)]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO opportunities
            (title, description, research_area, faculty_name, department,
             required_skills, available_positions, application_deadline, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data["title"], data["description"], data["research_area"],
            data["faculty_name"], data["department"], data["required_skills"],
            data["available_positions"], data["application_deadline"],
            data.get("status", "Open")
        )
        cursor.execute(query, values)
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Opportunity created", "id": new_id}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/opportunities", methods=["GET"])
def get_all_opportunities():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM opportunities")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/opportunities/<int:opportunity_id>", methods=["GET"])
def get_one_opportunity(opportunity_id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM opportunities WHERE id = %s", (opportunity_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if not result:
            return jsonify({"error": "Opportunity not found"}), 404
        return jsonify(result), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/opportunities/<int:opportunity_id>", methods=["PUT"])
def update_opportunity(opportunity_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM opportunities WHERE id = %s", (opportunity_id,))
        existing = cursor.fetchone()
        if not existing:
            cursor.close()
            conn.close()
            return jsonify({"error": "Opportunity not found"}), 404

        updated = {**existing, **data}
        query = """
            UPDATE opportunities SET
            title=%s, description=%s, research_area=%s, faculty_name=%s,
            department=%s, required_skills=%s, available_positions=%s,
            application_deadline=%s, status=%s
            WHERE id=%s
        """
        values = (
            updated["title"], updated["description"], updated["research_area"],
            updated["faculty_name"], updated["department"], updated["required_skills"],
            updated["available_positions"], updated["application_deadline"],
            updated["status"], opportunity_id
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Opportunity updated"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/opportunities/<int:opportunity_id>", methods=["DELETE"])
def delete_opportunity(opportunity_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM opportunities WHERE id = %s", (opportunity_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Opportunity not found"}), 404

        cursor.execute("DELETE FROM opportunities WHERE id = %s", (opportunity_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Opportunity deleted"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
