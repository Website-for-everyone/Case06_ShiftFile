"""
ShiftFile // FastAPI Backend & Static Server
Case 06 — Industrial In-Browser File Converter
"""
import io
import json
import csv
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from PIL import Image

app = FastAPI(title="ShiftFile API", version="1.0.4")

# Enable CORS for local testing & web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"


def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "app": "ShiftFile", "version": "1.0.4"}


@app.post("/api/convert/json-to-csv")
async def convert_json_to_csv(payload: List[Dict[str, Any]] | Dict[str, Any]):
    try:
        data = payload if isinstance(payload, list) else [payload]
        flattened_data = [flatten_dict(item) if isinstance(item, dict) else {"val": item} for item in data]
        if not flattened_data:
            return Response(content="", media_type="text/csv")

        # Collect unique headers
        headers = []
        for row in flattened_data:
            for k in row.keys():
                if k not in headers:
                    headers.append(k)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerows(flattened_data)
        csv_bytes = output.getvalue().encode("utf-8")

        return Response(
            content=csv_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=converted.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to convert JSON to CSV: {str(e)}")


@app.post("/api/convert/csv-to-json")
async def convert_csv_to_json(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        result = [row for row in reader]
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to convert CSV to JSON: {str(e)}")


@app.post("/api/convert/image")
async def convert_image(
    file: UploadFile = File(...),
    target_format: str = Form("png"),
    quality: int = Form(90)
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        fmt = target_format.lower()
        if fmt not in ["png", "jpeg", "jpg", "webp", "bmp"]:
            raise HTTPException(status_code=400, detail="Unsupported format")

        if fmt in ["jpeg", "jpg"] and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        output = io.BytesIO()
        save_format = "JPEG" if fmt in ["jpeg", "jpg"] else fmt.upper()
        image.save(output, format=save_format, quality=quality)
        output.seek(0)

        mime_map = {
            "png": "image/png",
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "webp": "image/webp",
            "bmp": "image/bmp"
        }

        return Response(
            content=output.getvalue(),
            media_type=mime_map[fmt],
            headers={"Content-Disposition": f"attachment; filename=converted.{fmt}"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image conversion failed: {str(e)}")


# Serve static web frontend
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8006, reload=False)
