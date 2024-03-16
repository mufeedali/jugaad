import re
import subprocess

from termcolor import colored, cprint
from termcolor._types import Color


def print_updates(status: str, color: Color, updates_list: list[str]):
    if updates_list:
        cprint(f"   {status}", color)
        for update in updates_list:
            print(f"     {update.strip()}")


def process_sbctl_output(output: str, regex_pattern: str, arg_list: list[str]):
    compiled_regex_pattern = re.compile(regex_pattern)
    success_list = []
    failure_list = []
    for line in output.splitlines():
        match = compiled_regex_pattern.search(line)
        if match:
            command_list = ["sbctl", *arg_list, match.group(1)]
            result = subprocess.run(command_list, check=True, capture_output=True, text=True)
            if not result.stderr:
                success_list.append(result.stdout)
            else:
                failure_list.append(result.stderr)

    return (success_list, failure_list)


if __name__ == "__main__":
    print(f"{colored('1', 'blue')}: Fetching list of EFI binaries...")
    result = subprocess.run(["sbctl", "verify"], check=True, capture_output=True, text=True)
    cprint("   List fetched.", "green")

    print(f"{colored('2', 'blue')}: Signing unsigned binaries...")
    sign_success_list, sign_failure_list = process_sbctl_output(result.stdout, r"✗ (.*)\sis", ["sign", "-s"])
    if sign_success_list or sign_failure_list:
        print_updates("Successfully signed:", "green", sign_success_list)
        print_updates("Failed signing with error:", "red", sign_failure_list)
    else:
        cprint("   All files signed.", "green")

    print(f"{colored('3', 'blue')}: Removing non-existent binaries from sbctl db...")
    rm_success_list, rm_failure_list = process_sbctl_output(result.stderr, r"‼ (.*)\sdoes", ["remove-file"])
    if rm_success_list or rm_failure_list:
        print_updates("Successfully removed:", "green", rm_success_list)
        print_updates("Failed removing with error:", "red", rm_failure_list)
    else:
        cprint("   No files to remove.", "green")
