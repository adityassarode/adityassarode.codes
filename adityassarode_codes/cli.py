import os
import shutil
import sys
import getpass
from importlib import resources

AUTHOR = "Aditya Sarode"
TOOL = "adityassarode.codes"
PACKAGE = "adityassarode_codes"

OWNER_USERNAME = "adityassarode"   # 👈 change if needed
OWNER_COMMAND = "__owner_list"     # hidden command


def is_owner():
    try:
        return getpass.getuser() == OWNER_USERNAME
    except Exception:
        return False


def banner():
    print("=" * 52)
    print(f"{TOOL}")
    print(f"Created by {AUTHOR}")
    print("=" * 52)


def owner_list_projects():
    if not is_owner():
        # silent fail – users never know this exists
        return

    templates_path = resources.files(PACKAGE).joinpath("templates")
    print("\n[OWNER MODE] Available projects:\n")

    for item in templates_path.iterdir():
        if item.is_dir():
            print(" -", item.name)


def init_project(project_name):
    banner()

    templates_path = resources.files(PACKAGE).joinpath("templates")
    src = templates_path.joinpath(project_name)

    if not src.exists():
        print("Error: project not found.")
        print("Contact the author for valid project names.")
        return

    dst = os.path.join(os.getcwd(), project_name)

    if os.path.exists(dst):
        print("Error: folder already exists:", project_name)
        return

    shutil.copytree(src, dst)

    print("\nProject downloaded successfully ✅")
    print("Author:", AUTHOR)
    print("Open with: code", project_name)


def main():
    # 🔒 hidden owner-only command
    if len(sys.argv) > 1 and sys.argv[1] == OWNER_COMMAND:
        owner_list_projects()
        return

    # normal user flow
    if len(sys.argv) < 3 or sys.argv[1] != "init":
        banner()
        print("Usage:")
        print("  adityassarode-codes init <project-name>")
        return

    init_project(sys.argv[2])


if __name__ == "__main__":
    main()
