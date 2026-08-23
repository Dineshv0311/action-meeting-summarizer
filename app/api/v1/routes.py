from flask import Blueprint, request, jsonify
from app.api.middlewares import validate_and_save_audio
from app.container import container
from app.core.exceptions import AppException

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

@api_v1_bp.route("/transcribe", methods=["POST"])
def transcribe_meeting():
    if "audio" not in request.files:
        return jsonify({"error": "Missing multipart form field 'audio'"}), 400

    uploaded_file = request.files["audio"]
    file_path = validate_and_save_audio(uploaded_file)
    result = container.meeting_service.process_transcription(file_path)

    return jsonify({
        "status": "success",
        "data": result.model_dump()
    }), 200

@api_v1_bp.route("/meetings/process", methods=["POST"])
def process_full_meeting():
    """Upload audio -> Transcribe -> Summarize -> Persist in SQLite."""
    if "audio" not in request.files:
        return jsonify({"error": "Missing multipart form field 'audio'"}), 400

    uploaded_file = request.files["audio"]
    title = request.form.get("title", None)

    file_path = validate_and_save_audio(uploaded_file)
    saved_record = container.meeting_service.process_and_save_meeting(file_path, title=title)

    return jsonify({
        "status": "success",
        "data": saved_record.model_dump()
    }), 201

@api_v1_bp.route("/meetings", methods=["GET"])
def get_all_meetings():
    """Fetch all stored meetings."""
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    records = container.meeting_service.list_meetings(limit=limit, offset=offset)
    return jsonify({
        "status": "success",
        "count": len(records),
        "data": [record.model_dump() for record in records]
    }), 200

@api_v1_bp.route("/meetings/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id: str):
    """Fetch a single meeting by UUID."""
    record = container.meeting_service.get_meeting_by_id(meeting_id)
    return jsonify({
        "status": "success",
        "data": record.model_dump()
    }), 200

@api_v1_bp.route("/meetings/<meeting_id>", methods=["DELETE"])
def delete_meeting(meeting_id: str):
    """Delete a meeting record."""
    container.meeting_service.delete_meeting(meeting_id)
    return jsonify({
        "status": "success",
        "message": f"Meeting '{meeting_id}' deleted successfully."
    }), 200

@api_v1_bp.app_errorhandler(AppException)
def handle_app_exception(error: AppException):
    return jsonify({"error": error.message}), error.status_code

@api_v1_bp.app_errorhandler(413)
def handle_file_too_large(error):
    return jsonify({"error": "File size exceeds the configured maximum limit."}), 413