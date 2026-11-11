
from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash
)

from db.connection import get_db_connection
from db.user import register_user, authenticate_user

app = Flask(__name__)
app.secret_key = "ganti-dengan-secret-sementara"


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = authenticate_user(email, password)

        if user:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        flash("Email atau password salah.")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or len(password) < 8:
            flash("Lengkapi data dan gunakan password minimal 8 karakter.")
            return redirect(url_for("register"))

        if register_user(username, email, password):
            flash("Registrasi berhasil. Silakan login.")
            return redirect(url_for("login"))

        flash("Username atau email sudah digunakan.")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("dashboard.html")

@app.route("/ticket/create")
def create_ticket():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("ticket_form.html")


@app.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("ticket_detail.html", ticket_id=ticket_id)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
