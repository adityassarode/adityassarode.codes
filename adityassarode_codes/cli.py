import os
import sys
import shutil
import getpass
import hashlib
import subprocess
import time
import threading
from importlib import resources

import requests

# =========================
# Metadata
# =========================
AUTHOR = "Aditya Sarode"
TOOL = "adityassarode.codes"
PACKAGE = "adityassarode_codes"

OWNER_PASSWORD_HASH = hashlib.sha256(
    b"Aditya@#2509"
).hexdigest()

# =========================
# GitHub Config
# =========================
GITHUB_OWNER = "adityassarode"
GITHUB_REPO = "adityassarode-codes"
GITHUB_BRANCH = "main"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents"
GITHUB_RAW = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{GITHUB_REPO}/{GITHUB_BRANCH}"

# =========================
# Colors
# =========================
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"

# =========================
# ASCII Logo
# =========================
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

# =========================
# Globals
# =========================
SELECTED_FILES = []

# =========================
# UI Helpers
# =========================
def banner():
    print(LOGO)


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
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")


def show_strict_notice_and_confirm():
    README_URL = "https://github.com/adityassarode/adityassarode.codes/blob/main/README.md"

    print(
        RED + BOLD +
        "\n============================================================\n"
        "IMPORTANT – READ BEFORE CONTINUING\n"
        "============================================================\n"
        + RESET
    )

    print(
        YELLOW +
        "Before using this tool, you MUST read and understand\n"
        "the rules, restrictions, and responsibility notice.\n\n"
        "Read the full notice here:\n\n"
        + RESET
        + CYAN + BOLD + README_URL + RESET + "\n"
    )

    print(
        RED + BOLD +
        "\n============================================================\n"
        + RESET
    )

    answer = input(
        YELLOW +
        "After reading the README, type YES to accept and continue: "
        + RESET
    ).strip().upper()

    if answer != "YES":
        print(
            RED + BOLD +
            "\nAccess denied. You must read and accept the README to continue.\n"
            + RESET
        )
        sys.exit(1)



# =========================
# Auth
# =========================
def owner_auth():
    try:
        pwd = getpass.getpass("🔐 Owner password: ")
        return hashlib.sha256(pwd.encode()).hexdigest() == OWNER_PASSWORD_HASH
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user.")
        sys.exit(1)



# =========================
# Paths
# =========================
def user_root():
    root = os.path.join(os.path.expanduser("~"), "adityassarode")
    os.makedirs(root, exist_ok=True)
    return root


# =========================
# Tree Printer
# =========================
def show_tree_with_icons(path, indent=""):
    for item in sorted(os.listdir(path)):
        full = os.path.join(path, item)
        if os.path.isdir(full):
            print(indent + "📂 " + item)
            show_tree_with_icons(full, indent + "  ")
        else:
            print(indent + "📄 " + item)

def parse_selection(choice, max_len):
    indexes = set()
    for part in choice.split(","):
        part = part.strip()
        if part.isdigit():
            i = int(part) - 1
            if 0 <= i < max_len:
                indexes.add(i)
    return sorted(indexes)


# =========================
# GitHub Logic
# =========================
def gh_list(path=""):
    try:
        r = requests.get(f"{GITHUB_API}/{path}", timeout=10)
        if r.status_code != 200:
            print(RED + "❌ Failed to load GitHub content." + RESET)
            return []
        return r.json()
    except requests.RequestException:
        print(RED + "❌ Network error while accessing GitHub." + RESET)
        return []



def gh_download(path):
    r = requests.get(f"{GITHUB_RAW}/{path}")
    return r.content if r.status_code == 200 else None


def browse_github():
    global SELECTED_FILES
    current = ""

    while True:
        items = gh_list(current)
        if not items:
            return

        print(YELLOW + f"\n📂 GitHub: /{current}\n" + RESET)

        entries = []

        for item in items:
            icon = "📂" if item["type"] == "dir" else "📄"
            print(f" {len(entries)+1}. {icon} {item['name']}")
            entries.append((item["type"], item["path"]))

        print("\n 0. 🔙 Go back")
        print(" ENTER → ⬇ Download selected files")

        choice = input("Select: ").strip()
        if choice == "":
            break

        if choice == "0":
            current = current.rsplit("/", 1)[0] if "/" in current else ""
            continue

        indexes = parse_selection(choice, len(entries))
        for i in indexes:
            kind, path = entries[i]
            if kind == "dir":
                current = path
            else:
                if path not in SELECTED_FILES:
                    SELECTED_FILES.append(path)



def download_github():
    root = user_root()

    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task,
        args=("⬇ Downloading selected files", stop_event),
    )
    spinner.start()

    for path in SELECTED_FILES:
        data = gh_download(path)
        if data:
            dst = os.path.join(root, path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "wb") as f:
                f.write(data)

    stop_event.set()
    spinner.join()

    post_download_output(root)

    


# =========================
# Local / Owner Templates
# =========================
def browse_local(base):
    global SELECTED_FILES
    current = base

    while True:
        print(YELLOW + f"\n📂 Local: {current.relative_to(base)}\n" + RESET)

        entries = []

        for item in current.iterdir():
            icon = "📂" if item.is_dir() else "📄"
            print(f" {len(entries)+1}. {icon} {item.name}")
            entries.append(item)

        print("\n 0. 🔙 Go back")
        print(" ENTER → ⬇ Download selected files")

        choice = input("Select: ").strip()
        if choice == "":
            break

        if choice == "0":
            if current != base:
                current = current.parent
            continue

        indexes = parse_selection(choice, len(entries))
        for i in indexes:
            item = entries[i]
            if item.is_dir():
                current = item
            else:
                if item not in SELECTED_FILES:
                    SELECTED_FILES.append(item)



def download_local(base):
    root = user_root()

    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task,
        args=("Downloading files", stop_event),
    )
    spinner.start()

    for f in SELECTED_FILES:
        dst = os.path.join(root, f.relative_to(base))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(f, dst)

    stop_event.set()
    spinner.join()

    post_download_output(root)

def ask_open_in_ide(path):
    print(
        YELLOW +
        "\n🧠 How would you like to open the downloaded files?\n"
        + RESET
    )
    print(" 1. 🟦 VS Code")
    print(" 2. 🟪 PyCharm")
    print(" 3. 📂 Open folder in file manager")
    print(" 0. ❌ Do nothing")

    choice = input("\nSelect option: ").strip()

    opened = False

    # 1️⃣ VS Code
    if choice == "1":
        try:
            subprocess.run(
                ["code", "--reuse-window", "-r", path],
                check=True
            )
            print(GREEN + "🚀 Opening in VS Code" + RESET)
            opened = True
        except Exception:
            print(RED + "❌ VS Code CLI not found." + RESET)

    # 2️⃣ PyCharm
    elif choice == "2":
        try:
            subprocess.run(["charm", path], check=True)
            print(GREEN + "🚀 Opening in PyCharm" + RESET)
            opened = True
        except Exception:
            print(RED + "❌ PyCharm CLI not available." + RESET)
            print(
                YELLOW +
                "ℹ️ Enable it in PyCharm: Tools → Create Command-line Launcher\n"
                + RESET
            )

    # 3️⃣ File manager (most reliable)
    elif choice == "3":
        try:
            if sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", path])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            elif sys.platform.startswith("win"):
                subprocess.Popen(["explorer", path])
            print(GREEN + "📂 Opening folder in file manager" + RESET)
            opened = True
        except Exception:
            pass

    # Always show path (ALL options)
    print(
        CYAN +
        "\n📁 Files are saved at:\n" +
        path +
        RESET
    )

    # Environment-specific hints
    if path.startswith("/root"):
        print(
            YELLOW +
            "📌 Google Colab detected: Open the Files panel on the left, "
            "expand the menu using the two dots (..), and open the folder named \"root\".\n"
            + RESET
        )

    if not opened:
        print(
            YELLOW +
            "ℹ️ Tip: You can open this path in any editor of your choice.\n"
            + RESET
        )


# =========================
# Final Output
# =========================
def post_download_output(root):
    print(GREEN + "\n✔ Download completed successfully" + RESET)
    print(CYAN + f"👤 Author: {AUTHOR}\n" + RESET)

    print(YELLOW + BOLD + "📂 Downloaded structure:" + RESET)
    print("📂 adityassarode")
    show_tree_with_icons(root, "  ")

    ask_open_in_ide(root)







# =========================
# GET Command
# =========================
def run_get():
    global SELECTED_FILES
    SELECTED_FILES = []

    banner()
    show_strict_notice_and_confirm()

    print("1. Browse and select GitHub files")
    print("2. Browse and select local files")
    print("3. Browse and select personal files")

    option = input("\nSelect option: ").strip()

    if option == "1":
        browse_github()
        download_github()

    elif option == "2":
        base = resources.files(PACKAGE).joinpath("templates")
        browse_local(base)
        download_local(base)

    elif option == "3":
        if not owner_auth():
            print(RED + "Access denied." + RESET)
            return
        base = resources.files(PACKAGE).joinpath("owner_templates")
        browse_local(base)
        download_local(base)


# =========================
# UPDATE Command
# =========================
def run_update():
    banner()
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", TOOL])
    print(GREEN + "\n✔ Update completed" + RESET)


# =========================
# MAIN
# =========================
def main():
    # Direct command handling
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "get":
            run_get()
            return

        if cmd == "update":
            run_update()
            return

        # Unknown command
        banner()
        print(RED + f"❌ Unknown command: {cmd}" + RESET)
        print("Run without arguments to see options.")
        return

    # Interactive menu (no arguments)
    banner()
    print(YELLOW + "What would you like to do?\n" + RESET)
    print(" 1. ⬇ Get / Download files")
    print(" 2. 🔄 Update this tool")
    print(" 3. ❌ Exit")

    choice = input("\nSelect an option (1/2/3): ").strip()

    if choice == "1":
        run_get()
    elif choice == "2":
        run_update()
    elif choice == "3":
        print(GREEN + "👋 Exiting. Have a nice day!" + RESET)
        sys.exit(0)
    else:
        print(RED + "❌ Invalid option. Please try again." + RESET)



if __name__ == "__main__":
    main()
