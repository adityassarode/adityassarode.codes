import os
import shutil
import sys
import getpass
import hashlib

import time
import threading
from importlib import resources

AUTHOR = "Aditya Sarode"
TOOL = "adityassarode.codes"
PACKAGE = "adityassarode_codes"
OWNER_PASSWORD_HASH = hashlib.sha256(
    b"Aditya@#2509"
).hexdigest()


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
            print(indent + CYAN + "📁 " + item + RESET)
            show_tree(full, indent + "  ")
        else:
            print(indent + GREEN + "📄 " + item + RESET)



def owner_auth():
    try:
        pwd = getpass.getpass("Owner password: ")
        return hashlib.sha256(pwd.encode()).hexdigest() == OWNER_PASSWORD_HASH
    except Exception:
        return False
    
def owner_templates_path():
    return resources.files(PACKAGE).joinpath("owner_templates")


# ===== Owner-only project list =====
def owner_list_projects():
    if not is_owner():
        return

    templates_path = resources.files(PACKAGE).joinpath("templates")
    print(YELLOW + "\n[OWNER MODE] Available projects:\n" + RESET)

    for item in templates_path.iterdir():
        if item.is_dir():
            print(" -", item.name)

def download_selected_files(project_name):
    banner()
    show_strict_notice_and_confirm()

    templates_path = resources.files(PACKAGE).joinpath("templates")
    src = templates_path.joinpath(project_name)

    if not src.exists():
        print(RED + "Project not found." + RESET)
        return

    files = [
        f for f in src.iterdir()
        if f.is_file() and not f.name.endswith(".pyc")
    ]

    if not files:
        print(YELLOW + "No files available to download." + RESET)
        return

    print(YELLOW + "\nAvailable files:\n" + RESET)
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.name}")

    choice = input(
        YELLOW + "\nEnter file numbers (comma separated): " + RESET
    ).strip()

    try:
        indexes = [int(x.strip()) - 1 for x in choice.split(",")]
    except ValueError:
        print(RED + "Invalid input." + RESET)
        return

    selected = []
    for i in indexes:
        if 0 <= i < len(files):
            selected.append(files[i])

    if not selected:
        print(RED + "No valid files selected." + RESET)
        return

    for f in selected:
        shutil.copy2(f, os.path.join(os.getcwd(), f.name))

    print(
        GREEN
        + f"\n✔ Downloaded {len(selected)} file(s) successfully"
        + RESET
    )

# ===== Preview project (NO download) =====
def preview_project(project_name):
    banner()
    show_strict_notice_and_confirm()
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
    show_strict_notice_and_confirm()
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
def owner_list():
    base = owner_templates_path()

    if not base.exists():
        print(YELLOW + "No owner projects found." + RESET)
        return

    print(YELLOW + "\n[OWNER] Available owner projects:\n" + RESET)

    for item in base.iterdir():
        if item.is_dir():
            print(" -", item.name)
def owner_view(project_name):
    base = owner_templates_path()
    src = base.joinpath(project_name)

    if not src.exists():
        print(RED + "Owner project not found." + RESET)
        return

    print(CYAN + "\n[OWNER] Project structure:\n" + RESET)
    show_tree(src)
def owner_get(project_name):
    base = owner_templates_path()
    src = base.joinpath(project_name)

    if not src.exists():
        print(RED + "Owner project not found." + RESET)
        return

    dst = os.path.join(os.getcwd(), project_name)

    if os.path.exists(dst):
        print(YELLOW + "Folder already exists." + RESET)
        return

    shutil.copytree(src, dst)
    print(GREEN + "✔ Owner project downloaded successfully" + RESET)
def owner_select(project_name):
    base = owner_templates_path()
    src = base.joinpath(project_name)

    if not src.exists():
        print(RED + "Owner project not found." + RESET)
        return

    files = [f for f in src.rglob("*") if f.is_file()]

    if not files:
        print(YELLOW + "No files found." + RESET)
        return

    print(YELLOW + "\nAvailable files:\n" + RESET)
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.relative_to(src)}")

    choice = input(
        YELLOW + "\nEnter numbers (comma separated): " + RESET
    ).strip()

    try:
        indexes = [int(x.strip()) - 1 for x in choice.split(",")]
    except ValueError:
        print(RED + "Invalid input." + RESET)
        return

    for i in indexes:
        if 0 <= i < len(files):
            dst = os.path.join(os.getcwd(), files[i].name)
            shutil.copy2(files[i], dst)

    print(GREEN + "✔ Selected files downloaded" + RESET)


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
    # ===== OWNER MODE =====
    if len(sys.argv) > 1 and sys.argv[1] == "-owner":
        banner()

        if not owner_auth():
            print(RED + "Access denied." + RESET)
            sys.exit(1)

        if len(sys.argv) > 2:
            cmd = sys.argv[2]

            if cmd == "list":
                owner_list()
                return

            if cmd == "view" and len(sys.argv) > 3:
                owner_view(sys.argv[3])
                return

            if cmd == "get" and len(sys.argv) > 3:
                owner_get(sys.argv[3])
                return

            if cmd == "select" and len(sys.argv) > 3:
                owner_select(sys.argv[3])
                return

        print(YELLOW + "Owner commands:" + RESET)
        print("  adityassarode-codes -owner list")
        print("  adityassarode-codes -owner view <project>")
        print("  adityassarode-codes -owner get <project>")
        print("  adityassarode-codes -owner select <project>")
        return

    # Owner-only hidden command
    if len(sys.argv) > 1 and sys.argv[1] == OWNER_COMMAND:
        owner_list_projects()
        return

    # Download selected files
    if len(sys.argv) > 2 and sys.argv[1] == "get":
        download_selected_files(sys.argv[2])
        return

    # Preview project
    if len(sys.argv) > 2 and sys.argv[1] == "preview":
        preview_project(sys.argv[2])
        return

    # Init project
    if len(sys.argv) > 2 and sys.argv[1] == "init":
        init_project(sys.argv[2])
        return

    # No arguments → interactive mode
    if len(sys.argv) == 1:
        project = interactive_select()
        init_project(project)
        return

    # Fallback / help
    banner()
    print("Usage:")
    print("  adityassarode-codes")
    print("  adityassarode-codes init <project>")
    print("  adityassarode-codes preview <project>")
    print("  adityassarode-codes get <project>")


if __name__ == "__main__":
    main()
