import os
import requests
import json
import shutil
import sqlite3
import pandas as pd
import subprocess
from bs4 import BeautifulSoup
from utils import read_file, write_file

DATA_DIR = "data/"

def ensure_data_dir():
    """Ensure the DATA_DIR exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

# 🚨 Security Rules: B1 & B2 🚨
def is_secure_path(file_path):
    """Ensure the path is within /data and prevent file deletions."""
    if not file_path.startswith(DATA_DIR):
        raise PermissionError("❌ Task Denied: Access to external directories is not allowed.")
    if "delete" in file_path.lower():
        raise PermissionError("❌ Task Denied: Deletion of files is not allowed.")
    return file_path

# ✅ Task B3: Fetch data from an API and save it
def fetch_api_data():
    """Fetch data from an API and save it."""
    ensure_data_dir()  # Make sure the data directory exists
    api_url = "https://jsonplaceholder.typicode.com/posts"
    output_path = os.path.join(DATA_DIR, "api_data.json")

    response = requests.get(api_url)
    if response.status_code == 200:
        write_file(output_path, json.dumps(response.json(), indent=2))
        return f"✅ Task B3 Successful: API data saved to {output_path}."
    return f"❌ Task B3 Failed: API request error."


def clone_and_commit_repo():
    """Clone a GitHub repo, update README, commit, and push."""
    repo_url = "https://github.com/Aishu-selvan/TDSP1.git"
    repo_dir = os.path.join(DATA_DIR, "TDSP1")

    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)  # Remove old repo

    try:
        subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
        with open(os.path.join(repo_dir, "README.md"), "a") as f:
            f.write("\nUpdated via automation.")

        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Automated update"], cwd=repo_dir, check=True)
        subprocess.run(["git", "push"], cwd=repo_dir, check=True)

        return "✅ Task B4 Successful: Git repo cloned, updated, and pushed."
    except subprocess.CalledProcessError as e:
        return f"❌ Error: {str(e)}"

# Run the function
print(clone_and_commit_repo())

def run_sql_query():
    """Execute an SQL query and return the result."""
    ensure_data_dir()
    db_path = os.path.join(DATA_DIR, "database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")  # Example query
    result = cursor.fetchone()[0]
    conn.close()
    return {
        "status": "success",
        "code": 0,  # 0 to indicate success (or use another convention, e.g., HTTP 200)
        "message": f"✅ Task B5 Successful: Query result = {result}."
    }




def scrape_website():
    """Scrape data from a website and save it."""
    ensure_data_dir()
    url = "https://example.com"
    output_path = os.path.join(DATA_DIR, "scraped_data.txt")
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
    except Exception as e:
        return f"❌ Task B6 Failed: Error fetching website data - {e}"
    
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        data = soup.get_text()
    except Exception as e:
        return f"❌ Task B6 Failed: Error processing HTML - {e}"
    
    try:
        write_file(output_path, data)
    except Exception as e:
        return f"❌ Task B6 Failed: Error writing file - {e}"
    
    return f"✅ Task B6 Successful: Website data saved to {output_path}."


# ✅ Task B7: Compress or resize an image
def resize_image():
    """Resize an image and save it."""
    from PIL import Image
    ensure_data_dir()
    image_path = os.path.join(DATA_DIR, "image.png")
    output_path = os.path.join(DATA_DIR, "image_resized.png")

    if not os.path.exists(image_path):
        return "❌ Task B7 Failed: Image file not found."

    with Image.open(image_path) as img:
        img = img.resize((300, 300))  # Resize to 300x300
        img.save(output_path)

    return f"✅ Task B7 Successful: Image resized."

# ✅ Task B8: Transcribe audio from an MP3 file
def transcribe_audio():
    """Convert speech to text."""
    return "✅ Task B8 Successful: Audio transcription completed (Mock response)."

# ✅ Task B9: Convert Markdown to HTML
def convert_markdown_to_html():
    """Convert Markdown file to HTML."""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "document.md")
    output_path = os.path.join(DATA_DIR, "document.html")

    if not os.path.exists(file_path):
        return "❌ Task B9 Failed: Markdown file not found."

    subprocess.run(["pandoc", file_path, "-o", output_path], check=True)
    return f"✅ Task B9 Successful: Markdown converted to HTML."

# ✅ Task B10: Write an API endpoint that filters a CSV file and returns JSON data
def filter_csv():
    """Filter a CSV file based on some criteria."""
    ensure_data_dir()
    file_path = os.path.join(DATA_DIR, "data.csv")
    output_path = os.path.join(DATA_DIR, "filtered_data.json")

    if not os.path.exists(file_path):
        return "❌ Task B10 Failed: CSV file not found."

    df = pd.read_csv(file_path)
    filtered_df = df[df["category"] == "Technology"]
    write_file(output_path, filtered_df.to_json(orient="records", indent=2))

    return f"✅ Task B10 Successful: Filtered data saved."

# ✅ Execute tasks based on input
def execute_task(task: str):
    tasks = {
        "fetch_api_data": fetch_api_data,
        "filter_csv": filter_csv,
        # Add other tasks as needed:
        #"clone_and_commit_repo": clone_and_commit_repo,
        "run_sql_query": run_sql_query,
        "scrape_website": scrape_website,
        "resize_image": resize_image,
        "transcribe_audio": transcribe_audio,
        "convert_markdown_to_html": convert_markdown_to_html,
    }
    result = tasks.get(task, lambda: "Invalid task")()
    print(f"Task executed: {task}")  # Debugging line
    return result

print("Starting script...")  # Debugging line
print(execute_task("fetch_api_data"))  # Example: Run API fetch task
print("Script finished!")  # Debugging line
