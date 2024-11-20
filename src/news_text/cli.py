import subprocess

def main():
    scripts = ["get_bbc_news.py", "upload_articles.py", "level_articles.py"]

    for script in scripts:
        try:
            print(f"Executing {script}...")
            subprocess.run(["python", script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing {script}: {e}")
            break

if __name__ == "__main__":
    main() 
