import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from .render import render_gg, render_gram, render_tme, render_ton

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

POOL = ThreadPoolExecutor(4)
RENDERERS = {
    "t.me": render_tme,
    "gram": render_gram,
    "ton": render_ton,
    "gg": render_gg,
}
LABEL = re.compile(r"^[a-z0-9]([a-z0-9_-]*[a-z0-9])?$")


def _validate(name: str) -> str:
    if not 1 <= len(name) <= 126:
        raise ValueError("name must be 1-126 characters")
    for label in name.split("."):
        if not LABEL.fullmatch(label):
            raise ValueError("each label must use a-z, 0-9, - and _, and start and end with a letter or digit")
    return name


@app.get("/health")
def health() -> Response:
    return Response(status_code=204)


@app.get("/{filename}")
async def dns_img(filename: str) -> Response:
    domain = filename.removesuffix(".webp")
    if domain == filename:  # one url per image, so a cache never stores it twice
        raise HTTPException(status_code=404, detail="the url must end in .webp")
    tld = next((t for t in RENDERERS if domain.endswith(f".{t}")), "ton")
    name = domain[: -len(tld) - 1] if domain.endswith(f".{tld}") else domain
    try:
        name = _validate(name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"invalid .{tld} name: {e}") from None
    body = await asyncio.get_running_loop().run_in_executor(POOL, RENDERERS[tld], name)
    return Response(
        body,
        media_type="image/webp",
        headers={"Cache-Control": "public, max-age=2592000, immutable"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
