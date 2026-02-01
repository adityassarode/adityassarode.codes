import os
import shutil
import sys

import time
import threading
from importlib import resources

AUTHOR = "Aditya Sarode"
TOOL = "adityassarode.codes"
PACKAGE = "adityassarode_codes"

OWNER_COMMAND = "__owner_list"

# ===== Colors =====
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"

# ===== ASCII Logo =====
LOGO = f"""
{CYAN}{BOLD}
   _      _ _ _              
  /_\  __| (_) |_ _  _ __ _  
 / _ \/ _` | |  _| || / _` | 
/_/_\_\__,_|_|\__|\_, \__,_| 
/ __| __ _ _ _ ___|__/| |___ 
\__ \/ _` | '_/ _ \/ _` / -_)
|___/\__,_|_| \___/\__,_\___|                                    

        adityassarode.codes
        by Aditya Sarode
{RESET}
"""


# ===== Owner check =====
def is_owner():
    return os.getenv("ADITYASSARODE") == "1"






# ===== Typing animation =====
def type_print(text, delay=0.01):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ===== Spinner animation =====
def spinner_task(message, stop_event):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(
            f"\r{YELLOW}{message} {frames[i % len(frames)]}{RESET}"
        )
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (len(message) + 6) + "\r")


# ===== Banner =====
def banner():
    print(LOGO)


# ===== Show folder tree =====
def show_tree(path, indent=""):
    for item in sorted(os.listdir(path)):
        if item == "__pycache__" or item.endswith(".pyc"):
            continue

        full = os.path.join(path, item)
        if os.path.isdir(full):
            print(indent + CYAN + "[DIR] " + item + RESET)
            show_tree(full, indent + "  ")
        else:
            print(indent + GREEN + "- " + item + RESET)




# ===== Owner-only project list =====
def owner_list_projects():
    if not is_owner():
        return

    templates_path = resources.files(PACKAGE).joinpath("templates")
    print(YELLOW + "\n[OWNER MODE] Available projects:\n" + RESET)

    for item in templates_path.iterdir():
        if item.is_dir():
            print(" -", item.name)


# ===== Preview project (NO download) =====
def preview_project(project_name):
    banner()
    templates_path = resources.files(PACKAGE).joinpath("templates")
    src = templates_path.joinpath(project_name)

    if not src.exists():
        print(RED + "Project not found." + RESET)
        return

    type_print(YELLOW + "👀 Previewing project \n" + RESET)
    show_tree(src)


# ===== Init project (download) =====
def init_project(project_name):
    banner()

    templates_path = resources.files(PACKAGE).joinpath("templates")
    src = templates_path.joinpath(project_name)

    if not src.exists():
        print(RED + "Error: project not found." + RESET)
        return

    dst = os.path.join(os.getcwd(), project_name)

    if os.path.exists(dst):
        print(YELLOW + "Folder already exists." + RESET)
        return

    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task,
        args=(f"Downloading {project_name}", stop_event),
    )
    spinner.start()

    time.sleep(0.6)
    shutil.copytree(src, dst)

    stop_event.set()
    spinner.join()

    print(GREEN + "✔ Project downloaded successfully" + RESET)

    print(CYAN + f"Author: {AUTHOR}\n" + RESET)

    print(YELLOW + BOLD + "📂 Project structure:" + RESET)
    show_tree(dst)

    print("\n" + CYAN + f"Open with: code {project_name}" + RESET)


# ===== Interactive selector =====
def interactive_select():
    templates = resources.files(PACKAGE).joinpath("templates")
    projects = sorted([p.name for p in templates.iterdir() if p.is_dir()])

    banner()
    print(YELLOW + "Select a project:\n" + RESET)

    for i, p in enumerate(projects, 1):
        print(f"  {i}. {p}")

    choice = input("\nEnter number: ").strip()

    if not choice.isdigit():
        print(RED + "Invalid selection." + RESET)
        sys.exit(1)

    idx = int(choice) - 1
    if idx < 0 or idx >= len(projects):
        print(RED + "Invalid selection." + RESET)
        sys.exit(1)

    return projects[idx]


# ===== Main =====
def main():
    if len(sys.argv) > 1 and sys.argv[1] == OWNER_COMMAND:
        owner_list_projects()
        return

    if len(sys.argv) == 1:
        project = interactive_select()
        init_project(project)
        return

    if sys.argv[1] == "preview" and len(sys.argv) > 2:
        preview_project(sys.argv[2])
        return

    if sys.argv[1] == "init" and len(sys.argv) > 2:
        init_project(sys.argv[2])
        return

    banner()
    print("Usage:")
    print("  adityassarode-codes")
    print("  adityassarode-codes init <project>")
    print("  adityassarode-codes preview <project>")


if __name__ == "__main__":
    main()
