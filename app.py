from flask import Flask, render_template, request, jsonify 
import sqlite3

app = Flask(__name__)
def init_db():
    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def seed_data():
    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM risks")
    count = cursor.fetchone()[0]

    if count == 0:
        risks = [
            ("Multiple failed login attempts", "Authentication", "High"),
            ("Unpatched software", "Software Security", "Medium"),
            ("Weak password policy", "Access Control", "Low")
        ]

        cursor.executemany(
            "INSERT INTO risks (name, category, severity) VALUES (?, ?, ?)",
            risks
        )

    conn.commit()
    conn.close()

@app.route("/add-risk", methods=["POST"])
def add_risk():
    data = request.get_json()

    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO risks (name, category, severity) VALUES (?, ?, ?)",
        (data["name"], data["category"], data["severity"])
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/delete-risk/<int:risk_id>", methods=["DELETE"])
def delete_risk(risk_id):
    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM risks WHERE id = ?", (risk_id,))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@app.route("/risks")
def risks():
    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, category, severity FROM risks")
    rows = cursor.fetchall()

    conn.close()

    risks = []

    for row in rows:
        risks.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "severity": row[3]
        })

    return render_template("risks.html", risks=risks)




@app.route("/")
def home():
    conn = sqlite3.connect("trusttrack.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM risks")
    total_risks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM risks WHERE severity = 'High'")
    high_risks = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_risks=total_risks,
        high_risks=high_risks
    )


    


if __name__ == "__main__":
    init_db()
    seed_data()
    app.run(debug=True)