from flask import (
    Flask, render_template, request,
    redirect, url_for, session, flash, abort
)

from security.encryption import encrypt_data, decrypt_data

from db.ticket import (
    get_user_tickets, 
    get_ticket,
    update_ticket,
    delete_ticket,
    create_ticket as save_ticket)
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

    tickets = get_user_tickets(
        session["user_id"],
        session["role"]
    )

    total_tickets = len(tickets)
    in_progress = sum(
        1 for ticket in tickets
        if ticket["status"] == "In Progress"
    )
    closed_tickets = sum(
        1 for ticket in tickets
        if ticket["status"] == "Closed"
    )

    return render_template(
        "dashboard.html",
        tickets=tickets,
        total_tickets=total_tickets,
        in_progress=in_progress,
        closed_tickets=closed_tickets
    )

@app.route("/ticket/create", methods=["GET", "POST"])
def create_ticket():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()

        if not title or not category or not description:
            flash("Semua kolom wajib diisi.")
            return redirect(url_for("create_ticket"))

        nonce, ciphertext = encrypt_data(description)

        save_ticket(
            session["user_id"],
            title,
            category,
            nonce,
            ciphertext
        )

        flash("Tiket berhasil dibuat.")
        return redirect(url_for("dashboard"))

    return render_template("ticket_form.html")

@app.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    ticket = get_ticket(
        ticket_id,
        session["user_id"],
        session["role"]
    )

    if ticket is None:
        abort(404)

    ticket["description"] = decrypt_data(
        ticket["description_nonce"],
        ticket["description"]
    )

    return render_template(
        "ticket_detail.html",
        ticket=ticket
    )

@app.route("/ticket/<int:ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    ticket = get_ticket(
        ticket_id,
        session["user_id"],
        session["role"]
    )

    if ticket is None:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "")
        description = request.form.get("description", "").strip()

        if (
            not title
            or len(title) > 100
            or category not in ("Technical", "Account", "General")
            or not description
        ):
            flash("Data tiket tidak valid.")
            return redirect(url_for("edit_ticket", ticket_id=ticket_id))

        nonce, ciphertext = encrypt_data(description)

        updated = update_ticket(
            ticket_id,
            session["user_id"],
            session["role"],
            title,
            category,
            nonce,
            ciphertext
        )

        if not updated:
            abort(404)

        flash("Tiket berhasil diperbarui.")
        return redirect(
            url_for("ticket_detail", ticket_id=ticket_id)
        )

    ticket["description"] = decrypt_data(
        ticket["description_nonce"],
        ticket["description"]
    )

    return render_template("ticket_form.html", ticket=ticket)

@app.route("/ticket/<int:ticket_id>/delete", methods=["POST"])
def remove_ticket(ticket_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    deleted = delete_ticket(
        ticket_id,
        session["user_id"],
        session["role"]
    )

    if not deleted:
        abort(404)

    flash("Tiket berhasil dihapus.")
    return redirect(url_for("dashboard"))

@app.route("/tickets")
def my_tickets():
    if "user_id" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    tickets = get_user_tickets(
        session["user_id"],
        session["role"]
    )

    if search:
        keyword = search.casefold()

        tickets = [
            ticket for ticket in tickets
            if keyword in ticket["title"].casefold()
            or keyword in ticket["category"].casefold()
            or keyword in ticket["status"].casefold()
            or keyword in ticket["username"].casefold()
        ]

    return render_template(
        "tickets.html",
        tickets=tickets,
        search=search
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
