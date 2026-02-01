import os
import sys
import subprocess
import time
import threading
import json

REQUIREMENTS_FILE = "requirements.txt"

# Exit codes
EXIT_OK = 0
EXIT_NO_REQUIREMENTS = 1
EXIT_CANCELLED = 2
EXIT_INSTALL_FAILED = 3

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
GRAY = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

SPINNER_FRAMES = ["|", "/", "-", "\\"]


def status(msg):
    print(f"{GREEN}[+]{RESET} {msg}")


def progress(msg):
    print(f"{BLUE}[+]{RESET} {msg}")


def warning(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def error(msg):
    print(f"{RED}[!]{RESET} {msg}")


def question(msg):
    return input(f"{CYAN}[?]{RESET} {msg}")


def get_python_version():
    return sys.version.split()[0]


def get_pip_version():
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.stdout.split()[1]
    except Exception:
        return "Unknown"


def parse_requirements(path):
    modules = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            name = (
                line.split("==")[0]
                .split(">=")[0]
                .split("<=")[0]
                .split("~=")[0]
            )
            modules.append(name)
    return modules


def spinner_task(stop_event, text):
    i = 0
    while not stop_event.is_set():
        frame = SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        print(f"\r{GRAY}{frame} {text}{RESET}", end="", flush=True)
        time.sleep(0.1)
        i += 1
    print("\r" + " " * 80 + "\r", end="", flush=True)


def bulk_check_installed(modules):
    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task,
        args=(stop_event, "Checking if modules are already installed..."),
    )
    spinner.start()

    installed = {}
    for m in modules:
        installed[m] = subprocess.run(
            [sys.executable, "-m", "pip", "show", m],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode == 0

    stop_event.set()
    spinner.join()
    return installed


def check_updates(modules):
    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task,
        args=(stop_event, "Checking for available updates..."),
    )
    spinner.start()

    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )

    stop_event.set()
    spinner.join()

    outdated = {}
    if result.returncode == 0:
        data = json.loads(result.stdout)
        for pkg in data:
            name = pkg["name"]
            if name in modules:
                outdated[name] = (pkg["version"], pkg["latest_version"])

    return outdated


def install_or_update(module, action_text):
    progress(f"{action_text} '{BOLD}{module}{RESET}'")

    start = time.perf_counter()
    stop_event = threading.Event()
    spinner = threading.Thread(
        target=spinner_task, args=(stop_event, "Working...")
    )
    spinner.start()

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", module],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    stop_event.set()
    spinner.join()

    elapsed = time.perf_counter() - start
    return result.returncode == 0, elapsed


def print_summary(summary):
    print(f"\n{BOLD}Installation Summary{RESET}")
    print("-" * 60)
    print(f"{'Module':18} {'Status':26} {'Time':8}")
    print("-" * 60)

    for name, status_text, elapsed in summary:
        time_str = f"{elapsed:.2f}s" if elapsed is not None else "-"
        print(f"{name:18} {status_text:26} {time_str:8}")

    print("-" * 60)


def main():
    summary = []

    print(f"\n{BOLD}---- Sketcha Requirements Installer ----{RESET}\n")
    print(f"pip version      :  {get_pip_version()}")
    print(f"python version   :  {get_python_version()}\n")

    print(f"{GREEN}[+]{RESET} Looking for 'requirements.txt' file...", end="")
    if not os.path.isfile(REQUIREMENTS_FILE):
        print(f" {RED}NOT FOUND{RESET}")
        sys.exit(EXIT_NO_REQUIREMENTS)
    print(f" {GREEN}FOUND{RESET}")

    warning("Parsing requirements file...")
    modules = parse_requirements(REQUIREMENTS_FILE)

    installed_map = bulk_check_installed(modules)
    installed = [m for m in modules if installed_map[m]]
    missing = [m for m in modules if not installed_map[m]]

    if installed:
        warning("Already installed: " + ", ".join(installed))

    updates = {}
    if installed:
        updates = check_updates(installed)
        if updates:
            warning(
                "Updates available: "
                + ", ".join(
                    f"{k} ({v[0]} → {v[1]})" for k, v in updates.items()
                )
            )

            if question("Install available updates? (Y/n) ").strip().lower() != "n":
                for mod in updates:
                    ok, elapsed = install_or_update(mod, "Updating module")
                    if not ok:
                        summary.append((mod, "Update failed", elapsed))
                        sys.exit(EXIT_INSTALL_FAILED)
                    summary.append((mod, "Updated", elapsed))
            else:
                for mod in updates:
                    summary.append((mod, "Update skipped", None))

    if not missing and not updates:
        warning("All modules are already installed.")
        for m in installed:
            summary.append((m, "Already installed", None))
        print_summary(summary)
        print(f"\n{GREEN}[+]{RESET} {BOLD}Done! Now safe to launch app!{RESET}")
        sys.exit(EXIT_OK)

    if missing:
        status("Modules to be installed: " + ", ".join(missing))
        if question("Do you agree to continue? (Y/n) ").strip().lower() == "n":
            sys.exit(EXIT_CANCELLED)

        for mod in missing:
            ok, elapsed = install_or_update(mod, "Installing module")
            if not ok:
                summary.append((mod, "Install failed", elapsed))
                sys.exit(EXIT_INSTALL_FAILED)
            summary.append((mod, "Installed", elapsed))

    for m in installed:
        if m not in updates:
            summary.append((m, "Already installed", None))

    print_summary(summary)
    print(f"\n{GREEN}[+]{RESET} {BOLD}Done! Now safe to launch app!{RESET}")
    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()
