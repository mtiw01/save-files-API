import json
import mimetypes
import urllib.request
import uuid
from pathlib import Path


API_URL = "http://127.0.0.1:8000"


def send(file_path=None, message=None):
    if file_path is None and message is None:
        raise ValueError("Provide a file, a message, or both.")

    boundary = uuid.uuid4().hex
    body = bytearray()

    # Add message
    if message is not None:
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            b'Content-Disposition: form-data; name="message"\r\n\r\n'
        )
        body.extend(message.encode("utf-8"))
        body.extend(b"\r\n")

    # Add file
    if file_path is not None:
        file_path = Path(file_path)

        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        filename = file_path.name

        content_type = mimetypes.guess_type(filename)[0]
        if content_type is None:
            content_type = "application/octet-stream"

        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode()
        )
        body.extend(f"Content-Type: {content_type}\r\n\r\n".encode())

        body.extend(file_path.read_bytes())
        body.extend(b"\r\n")

    # End multipart data
    body.extend(f"--{boundary}--\r\n".encode())

    request = urllib.request.Request(
        f"{API_URL}/send",
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))