from pathlib import Path
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Video, Comment, Like
from app.storage import save_video

videos = Blueprint("videos", __name__, url_prefix="/videos")

@videos.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        file = request.files.get("video")

        if not title:
            flash("Please enter a title.", "danger")
            return redirect(url_for("videos.upload"))

        try:
            video_url, storage_type = save_video(file)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("videos.upload"))
        except Exception as exc:
            current_app.logger.exception("Video upload failed")
            flash(f"Video upload failed: {exc}", "danger")
            return redirect(url_for("videos.upload"))

        video = Video(
            title=title,
            description=description,
            video_url=video_url,
            storage_type=storage_type,
            user_id=current_user.id,
        )
        db.session.add(video)
        db.session.commit()

        flash("Video uploaded successfully.", "success")
        return redirect(url_for("videos.watch", video_id=video.id))

    return render_template("upload.html")

@videos.route("/<int:video_id>")
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()

    user_has_liked = False
    if current_user.is_authenticated:
        user_has_liked = Like.query.filter_by(
            user_id=current_user.id,
            video_id=video.id
        ).first() is not None

    return render_template(
        "video_detail.html",
        video=video,
        user_has_liked=user_has_liked,
    )

@videos.route("/<int:video_id>/comment", methods=["POST"])
@login_required
def add_comment(video_id):
    video = Video.query.get_or_404(video_id)
    content = request.form.get("content", "").strip()

    if not content:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("videos.watch", video_id=video.id))

    comment = Comment(
        content=content,
        user_id=current_user.id,
        video_id=video.id,
    )
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("videos.watch", video_id=video.id))

@videos.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        flash("You can only delete your own comments.", "danger")
        return redirect(url_for("videos.watch", video_id=comment.video_id))

    video_id = comment.video_id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "success")
    return redirect(url_for("videos.watch", video_id=video_id))

@videos.route("/<int:video_id>/like", methods=["POST"])
@login_required
def toggle_like(video_id):
    video = Video.query.get_or_404(video_id)
    existing = Like.query.filter_by(
        user_id=current_user.id,
        video_id=video.id
    ).first()

    if existing:
        db.session.delete(existing)
    else:
        db.session.add(Like(user_id=current_user.id, video_id=video.id))

    db.session.commit()
    return redirect(url_for("videos.watch", video_id=video.id))

@videos.route("/<int:video_id>/delete", methods=["POST"])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)

    if video.user_id != current_user.id:
        flash("You can only delete your own videos.", "danger")
        return redirect(url_for("videos.watch", video_id=video.id))

    if video.storage_type == "local":
        try:
            filename = video.video_url.rsplit("/", 1)[-1]
            path = Path(current_app.config["UPLOAD_FOLDER"]) / filename
            if path.exists():
                path.unlink()
        except Exception:
            current_app.logger.exception("Could not remove local video file")

    db.session.delete(video)
    db.session.commit()
    flash("Video deleted.", "success")
    return redirect(url_for("main.index"))
