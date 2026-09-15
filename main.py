from pathlib import Path
from datetime import datetime
import json

from fastapi import FastAPI, File, Form, UploadFile


app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/send")
async def send(
    message: str | None = Form(None),
    file: UploadFile | None = File(None)
):
    # Require at least a message or a file
    if message is None and file is None:
        return {
            "error": "You must provide a message, a file, or both."
        }

    # One timestamp for everything in this request
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    saved_files = []

    # Save the uploaded file
    if file is not None:
        filename = Path(file.filename).name
        file_path = UPLOAD_DIR / f"{timestamp}-{filename}"

        with file_path.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        saved_files.append(file_path.name)

    # Save the message
    if message is not None:
        message_path = UPLOAD_DIR / f"{timestamp}-message.json"

        message_data = {
            "message": message
        }

        with message_path.open("w", encoding="utf-8") as f:
            json.dump(message_data, f, indent=4, ensure_ascii=False)

        saved_files.append(message_path.name)

    return {
        "message": "Data saved successfully",
        "files": saved_files
    }