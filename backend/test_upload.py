"""Quick end-to-end test script — uploads a real image and prints the result."""
import json
import urllib.request
from urllib.request import Request

img_path = r"data\clean\clean_0001.jpg"
with open(img_path, "rb") as f:
    img_data = f.read()

boundary = "boundary123456"
nl = b"\r\n"
body = (
    b"--" + boundary.encode() + nl
    + b'Content-Disposition: form-data; name="file"; filename="clean_0001.jpg"' + nl
    + b"Content-Type: image/jpeg" + nl + nl
    + img_data + nl
    + b"--" + boundary.encode() + b"--" + nl
)

req = Request(
    "http://localhost:8000/analyze",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())

print("quality_score :", result["quality_score"])
print("quality_label :", result["quality_label"])
print("issues        :", result["issues"])
print("thumbnail_url :", result["thumbnail_url"])
print("heatmap rows  :", len(result["heatmap"]))
print("features      :", list(result["features"].keys()))
