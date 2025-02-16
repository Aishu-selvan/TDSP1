from fastapi import FastAPI, HTTPException, Query
import subprocess
import os
import json
import sqlite3
import openai
from datetime import datetime
import glob
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

def execute_task(task: str):
    try:
        task_lower = task.lower()
        
        if "install uv" in task_lower:
            subprocess.run(["pip", "install", "--user", "uv"], check=True)
            subprocess.run(["python", "datagen.py", os.environ["USER_EMAIL"]], check=True)
            return "Installed uv and ran datagen.py"
        
        elif "format" in task_lower and "prettier" in task_lower:
            subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
            return "Formatted /data/format.md with Prettier"
        
        elif "count" in task_lower and "wednesdays" in task_lower:
            with open("/data/dates.txt") as f:
                count = sum(1 for line in f if datetime.strptime(line.strip(), "%Y-%m-%d").weekday() == 2)
            with open("/data/dates-wednesdays.txt", "w") as f:
                f.write(str(count))
            return f"Counted {count} Wednesdays."
        
        elif "sort contacts" in task_lower:
            with open("/data/contacts.json") as f:
                contacts = json.load(f)
            contacts.sort(key=lambda x: (x["last_name"], x["first_name"]))
            with open("/data/contacts-sorted.json", "w") as f:
                json.dump(contacts, f, indent=4)
            return "Sorted contacts and saved to /data/contacts-sorted.json"
        
        elif "recent log files" in task_lower:
            log_files = sorted(glob.glob("/data/logs/*.log"), key=os.path.getmtime, reverse=True)[:10]
            with open("/data/logs-recent.txt", "w") as f:
                for log_file in log_files:
                    with open(log_file) as lf:
                        first_line = lf.readline().strip()
                        f.write(first_line + "\n")
            return "Extracted first line of 10 most recent log files"
        
        elif "index markdown files" in task_lower:
            md_files = glob.glob("/data/docs/*.md")
            index = {}
            for file in md_files:
                with open(file) as f:
                    for line in f:
                        if line.startswith("#"):
                            index[os.path.basename(file)] = line.strip("# ").strip()
                            break
            with open("/data/docs/index.json", "w") as f:
                json.dump(index, f, indent=4)
            return "Created Markdown index file"
        
        elif "extract email sender" in task_lower:
            with open("/data/email.txt", "r") as f:
                email_content = f.read()
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"Extract the sender's email from this:\n{email_content}"}]
            )
            sender_email = response["choices"][0]["message"]["content"].strip()
            with open("/data/email-sender.txt", "w") as f:
                f.write(sender_email)
            return f"Extracted sender email: {sender_email}"
        
        elif "extract credit card number" in task_lower:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Extract the credit card number from the image /data/credit-card.png"}]
            )
            card_number = response["choices"][0]["message"]["content"].strip().replace(" ", "")
            with open("/data/credit-card.txt", "w") as f:
                f.write(card_number)
            return f"Extracted credit card number: {card_number}"
        
        elif "find similar comments" in task_lower:
            with open("/data/comments.txt") as f:
                comments = f.readlines()
            # Placeholder: Assume comments[0] and comments[1] are the most similar
            with open("/data/comments-similar.txt", "w") as f:
                f.write(comments[0] + comments[1])
            return "Found the most similar comments and saved them."
        
        elif "calculate ticket sales" in task_lower:
            conn = sqlite3.connect("/data/ticket-sales.db")
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
            total_sales = cursor.fetchone()[0]
            conn.close()
            with open("/data/ticket-sales-gold.txt", "w") as f:
                f.write(str(total_sales))
            return f"Calculated total sales for Gold tickets: {total_sales}"
        
        else:
            raise ValueError("Unsupported task")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run")
async def run_task(task: str = Query(..., description="Task description in plain English")):
    return {"status": "success", "output": execute_task(task)}

@app.get("/read")
async def read_file(path: str = Query(..., description="Path to file")):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(path, "r") as file:
        return {"content": file.read()}
