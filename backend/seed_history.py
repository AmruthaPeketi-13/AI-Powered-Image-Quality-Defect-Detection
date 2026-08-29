"""Seed history with 3 sample images so the history page has data."""
import json
import os
import glob
import urllib.request
from urllib.request import Request


def upload(path, name):
    with open(path, "rb") as f:
        data = f.read()
    boundary = "boundary999abc"
    nl = b"\r\n"
    disposition = f'Content-Disposition: form-data; name="file"; filename="{name}"'.encode()
    body = (
        b"--" + boundary.encode() + nl
        + disposition + nl
        + b"Content-Type: image/jpeg" + nl + nl
        + data + nl
        + b"--" + boundary.encode() + b"--" + nl
    )
    req = Request(
        "http://localhost:8000/analyze",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    res = json.loads(urllib.request.urlopen(req).read())
    print(f"  {name} -> {res['quality_label']} (score={res['quality_score']}) thumb={res['thumbnail_url']}")


images = sorted(glob.glob(r"data\clean\*.jpg"))[:4]
print(f"Uploading {len(images)} sample images...")
for img in images:
    upload(img, os.path.basename(img))
print("Done.")
