from flask import Flask, render_template, request, redirect
import psycopg2
from psycopg2.extras import RealDictCursor

import os
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            location TEXT,
            date_applied TEXT,
            status TEXT NOT NULL,
            job_url TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/")
def home():
    search = request.args.get("search", "")
    status = request.args.get("status", "")

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT * FROM applications
        WHERE 1 = 1
    """

    params = []

    if search:
        query += """
            AND (
                company ILIKE %s
                OR role ILIKE %s
                OR location ILIKE %s
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

    if status:
        query += " AND status = %s"
        params.append(status)

    query += " ORDER BY id DESC"

    cursor.execute(query, params)
    applications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        applications=applications,
        search=search,
        status=status
    )


@app.route("/add", methods=["GET", "POST"])
def add_application():
    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date_applied = request.form["date_applied"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO applications
            (
                company,
                role,
                location,
                date_applied,
                status,
                job_url,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            company,
            role,
            location,
            date_applied,
            status,
            job_url,
            notes
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    return render_template("add.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_application(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute(
        "SELECT * FROM applications WHERE id = %s",
        (id,)
    )

    application = cursor.fetchone()

    if request.method == "POST":
        company = request.form["company"]
        role = request.form["role"]
        location = request.form["location"]
        date_applied = request.form["date_applied"]
        status = request.form["status"]
        job_url = request.form["job_url"]
        notes = request.form["notes"]

        cursor.execute("""
            UPDATE applications
            SET
                company = %s,
                role = %s,
                location = %s,
                date_applied = %s,
                status = %s,
                job_url = %s,
                notes = %s
            WHERE id = %s
        """, (
            company,
            role,
            location,
            date_applied,
            status,
            job_url,
            notes,
            id
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect("/")

    cursor.close()
    conn.close()

    return render_template(
        "edit.html",
        application=application
    )


@app.route("/delete/<int:id>", methods=["POST"])
def delete_application(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM applications WHERE id = %s",
        (id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)