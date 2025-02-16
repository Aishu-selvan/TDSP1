import json
import logging
import asyncio
import httpx

import os
import subprocess
from PIL import Image
import sqlite3, duckdb

async def run(task: str):
    async with httpx.AsyncClient(timeout=30) as client:
        logging.warning(f"🟡 Running task: {task.strip()}")
        response = await client.post("http://localhost:8000/run", params={"task": task})
        try:
            response_text = json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            response_text = response.text
        if response.status_code < 400:
            logging.info(f"🟢 HTTP {response.status_code} {response_text}")
        else:
            logging.error(f"🔴 HTTP {response.status_code} {response_text}")
        return response.status_code, response_text

async def read(path: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(f"http://localhost:8000/read?path={path}")
        if response.status_code != 200:
            raise Exception(f"Cannot read {path}")
        return response.text

async def b3(email, **kwargs):
    await run("Fetch data from https://jsonplaceholder.typicode.com/posts and save it to /data/api_data.json")
    result = await read("/data/api_data.json")
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        return False
    return isinstance(data, list) and len(data) > 0

async def b5(email, **kwargs):
    query = "SELECT 1"
    db_path = "/data/test.db"
    output_file = "/data/query_result.txt"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
    conn.commit()
    conn.close()
    await run(f"Run SQL query '{query}' on {db_path} and save output to {output_file}")
    result = await read(output_file)
    return "[(1,)]" in result

async def b6(email, **kwargs):
    await run("Fetch content from https://news.ycombinator.com/ and save it to /data/scraped_data.txt")
    scraped_content = await read("/data/scraped_data.txt")
    return bool(scraped_content.strip()) and "Hacker News" in scraped_content

async def b7(email, **kwargs):
    image_path = "/data/input.jpg"
    output_path = "/data/output.jpg"
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_path)
    await run(f"Resize {image_path} to 50x50 and save to {output_path}")
    try:
        img_resized = Image.open(output_path)
        return img_resized.size == (50, 50)
    except FileNotFoundError:
        return False

async def b9(email, **kwargs):
    md_path = "/data/input.md"
    output_path = "/data/output.html"
    with open(md_path, "w") as f:
        f.write("# Title\n\nThis is a test.")
    await run(f"Convert Markdown {md_path} to HTML and save in {output_path}")
    result = await read(output_path)
    return "<h1>Title</h1>" in result

async def main(email: str):
    tasks = [b3, b5, b6, b7, b9]
    score, total = 0, len(tasks)
    for task in tasks:
        try:
            success = await task(email=email)
        except Exception as e:
            logging.error(f"🔴 {task.__name__.upper()} failed: {e}")
            success = False
        if success:
            logging.info(f"✅ {task.__name__.upper()} PASSED")
        else:
            logging.error(f"❌ {task.__name__.upper()} FAILED")
        score += 1 if success else 0
    logging.info(f"🎯 Score: {score} / {total}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="user@example.com")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(main(args.email))
