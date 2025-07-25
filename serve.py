from typing import Union

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from starlette.concurrency import run_in_threadpool
import asyncio
import instagram

app = FastAPI()
inst = instagram.Instagram()
EMBED_USERAGENTS = ["TelegramBot (like TwitterBot)", "chatterino-api-cache/2.1.0 link-resolver", "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    while True:
        await asyncio.sleep(3600)

async def handle_request(post_id):
    post_data = await run_in_threadpool(inst.handle_post, post_id)
    conn, response = await run_in_threadpool(inst.get_http_video_response, post_data[0])
    generator = inst.stream_chunks(response)
    return StreamingResponse(generator(), media_type=post_data[1])

async def check_header(request: Request):
    ua = request.headers.get("User-Agent")
    return ua in EMBED_USERAGENTS

@app.get("/p/{post_id}")
async def read_post(post_id:str, request:Request):
    if(not await check_header(request)): return RedirectResponse(url=f"https://instagram.com/p/{post_id}")
    return await handle_request(post_id)

@app.get("/reels/{post_id}")
async def read_post(post_id:str, request:Request):
    if(not await check_header(request)): return RedirectResponse(url=f"https://instagram.com/reels/{post_id}")
    return await handle_request(post_id)

@app.get("/reel/{post_id}")
async def read_post(post_id:str, request:Request):
    if(not await check_header(request)): return RedirectResponse(url=f"https://instagram.com/reel/{post_id}")
    return await handle_request(post_id)

@app.get("/{username}/reel/{post_id}")
async def read_post(username:str, post_id:str, request:Request):
    if(not await check_header(request)): return RedirectResponse(url=f"https://instagram.com/{username}/reel/{post_id}")
    return await handle_request(post_id)

@app.get("/{username}/p/{post_id}")
async def read_post(username:str, post_id:str, request:Request):
    if(not await check_header(request)): return RedirectResponse(url=f"https://instagram.com/{username}/p/{post_id}")
    return await handle_request(post_id)

@app.exception_handler(404)
async def fourofour(_, __):
    while True: await asyncio.sleep(3600)