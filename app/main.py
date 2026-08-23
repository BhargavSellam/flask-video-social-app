from flask import Blueprint, render_template, request
from app.models import Video, User

main = Blueprint("main", __name__)

@main.route("/")
def index():
    q = request.args.get("q", "").strip()
    query = Video.query
    if q:
        query = query.filter(
            Video.title.ilike(f"%{q}%") |
            Video.description.ilike(f"%{q}%")
        )
    videos = query.order_by(Video.created_at.desc()).all()
    return render_template("index.html", videos=videos, q=q)

@main.route("/profile/<username>")
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.created_at.desc()).all()
    return render_template("profile.html", profile_user=user, videos=videos)
