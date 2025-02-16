import subprocess

def format_markdown(prettier_version="prettier@3.4.2", filename="/data/format.md"):
    """Formats a markdown file using Prettier."""
    command = [r"C:\Program Files\nodejs\npx.cmd", prettier_version, "--write", filename]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Prettier executed successfully on {filename}.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred while running Prettier: {e}")

# Run the function directly
if __name__ == "_main_":
    format_markdown()