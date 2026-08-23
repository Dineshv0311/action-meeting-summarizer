from pathlib import Path
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app.core.config import settings
from app.core.exceptions import FileValidationError

def validate_and_save_audio(file: FileStorage) -> Path:
    if not file or file.filename == "":
        raise FileValidationError("No audio file provided in request.")

    filename = secure_filename(file.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in settings.ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"Unsupported file format '.{extension}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    destination = settings.UPLOAD_DIR / filename
    file.save(destination)
    return destination