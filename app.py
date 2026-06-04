from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Social Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Social Downloader API"
    }


@app.get("/download")
def download(url: str):

    try:
        ydl_opts = {
            "quiet": True,
            "noplaylist": True,
            "extract_flat": False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        seen = set()

        for f in info.get("formats", []):

            height = f.get("height")
            download_url = f.get("url")

            if not height or not download_url:
                continue

            quality = f"{height}p"

            # تجاهل التكرارات
            if quality in seen:
                continue

            seen.add(quality)

            formats.append({
                "quality": quality,
                "ext": f.get("ext", "mp4"),
                "filesize": f.get("filesize"),
                "url": download_url
            })

        # ترتيب الجودات من الأعلى إلى الأقل
        formats = sorted(
            formats,
            key=lambda x: int(x["quality"].replace("p", "")),
            reverse=True
        )

        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "formats": formats
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
