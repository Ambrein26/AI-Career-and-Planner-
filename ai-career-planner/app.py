from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from extensions import db
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Ensure instance and upload folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "static", "uploads"), exist_ok=True)

    db.init_app(app)

    from models.user_model import User
    from models.career_model import Career

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return redirect(url_for("signup"))

            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please log in.", "warning")
                return redirect(url_for("login"))

            hashed = generate_password_hash(password)
            user = User(email=email, password_hash=hashed)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                flash("Logged in successfully.", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid credentials.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            return redirect(url_for("login"))
        return render_template("dashboard.html")

    @app.route("/upload-resume", methods=["GET", "POST"])
    def upload_resume():
        if "user_id" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            file = request.files.get("resume")
            if not file:
                flash("Please upload a resume file.", "warning")
                return redirect(url_for("upload_resume"))

            upload_folder = os.path.join(app.root_path, "static", "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, file.filename)
            file.save(filepath)

            # TODO: integrate resume parsing and skill extraction
            session["uploaded_resume_path"] = filepath
            flash("Resume uploaded successfully.", "success")
            return redirect(url_for("career_selection"))

        return render_template("upload_resume.html")

    @app.route("/career-selection", methods=["GET", "POST"])
    def career_selection():
        if "user_id" not in session:
            return redirect(url_for("login"))
        # TODO: Load careers from database/careers.json
        careers = []
        if request.method == "POST":
            chosen = request.form.get("career")
            session["target_career"] = chosen
            return redirect(url_for("results"))
        return render_template("career_selection.html", careers=careers)

    @app.route("/results")
    def results():
        if "user_id" not in session:
            return redirect(url_for("login"))
        # TODO: Perform skill gap analysis and show recommendations
        return render_template("results.html")

    @app.route("/roadmap")
    def roadmap():
        if "user_id" not in session:
            return redirect(url_for("login"))
        # TODO: Generate personalized roadmap
        return render_template("roadmap.html")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)


