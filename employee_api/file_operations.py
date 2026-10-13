# file_operations.py
# This file contains all file handling logic for text files.
# Every function works only inside the 'uploads' folder.
# Users cannot read, write, or delete files outside that folder.

import os
import shutil

# This is the absolute path to the uploads folder.
# os.path.dirname(__file__) gives the folder where this file lives.
# os.path.join then adds 'uploads' to that path.
UPLOADS_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")


def get_safe_path(filename: str) -> str:
    """
    Build a full file path and verify it stays inside UPLOADS_FOLDER.

    Why this matters:
    A user could send filename = "../../etc/passwd" to try to access
    system files. os.path.abspath resolves all '..' and gives the real path.
    We then check that the real path starts with UPLOADS_FOLDER.
    If it doesn't, we raise an error immediately.
    """
    # Join the uploads folder path with the filename
    full_path = os.path.join(UPLOADS_FOLDER, filename)

    # Resolve the absolute real path (removes any '..' tricks)
    safe_path = os.path.abspath(full_path)

    # Check that the resolved path is still inside UPLOADS_FOLDER
    if not safe_path.startswith(os.path.abspath(UPLOADS_FOLDER)):
        raise ValueError("Access denied: file path is outside the uploads folder.")

    return safe_path


# ─────────────────────────────────────────────
# 1. CREATE A FILE
# ─────────────────────────────────────────────
def create_file(filename: str) -> str:
    """
    Create an empty file inside uploads/.
    If the file already exists, raise an error.

    'x' mode means: create the file, but fail if it already exists.
    This prevents accidentally overwriting an existing file.
    """
    path = get_safe_path(filename)

    if os.path.exists(path):
        raise FileExistsError(f"File '{filename}' already exists.")

    with open(path, "x", encoding="utf-8") as file:
        pass  # We just want to create an empty file, nothing to write

    return f"File '{filename}' created successfully."


# ─────────────────────────────────────────────
# 2. WRITE TO A FILE (overwrites existing content)
# ─────────────────────────────────────────────
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file, replacing everything that was there before.

    'w' mode: open for writing. Creates the file if it doesn't exist.
    If the file exists, it is OVERWRITTEN completely.
    """
    path = get_safe_path(filename)

    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

    return f"Content written to '{filename}' successfully."


# ─────────────────────────────────────────────
# 3. APPEND TO A FILE (adds to existing content)
# ─────────────────────────────────────────────
def append_file(filename: str, content: str) -> str:
    """
    Add content to the END of a file without touching what's already there.

    'a' mode: open for appending. Creates the file if it doesn't exist.
    The file pointer starts at the end, so new content goes after old content.
    """
    path = get_safe_path(filename)

    with open(path, "a", encoding="utf-8") as file:
        file.write(content)

    return f"Content appended to '{filename}' successfully."


# ─────────────────────────────────────────────
# 4. READ FULL FILE
# ─────────────────────────────────────────────
def read_file_full(filename: str) -> str:
    """
    Read and return the entire content of a file as a single string.

    'r' mode: open for reading (this is the default mode).
    file.read() returns everything in one string.
    """
    path = get_safe_path(filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    return content


# ─────────────────────────────────────────────
# 5. READ FILE LINE BY LINE
# ─────────────────────────────────────────────
def read_file_lines(filename: str) -> list:
    """
    Read a file and return each line as an item in a list.

    file.readlines() returns a list like:
    ["line one\n", "line two\n", "line three"]

    We use strip() on each line to remove the trailing newline character.
    """
    path = get_safe_path(filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    with open(path, "r", encoding="utf-8") as file:
        # Strip each line to remove '\n' at the end
        lines = [line.strip() for line in file.readlines()]

    return lines


# ─────────────────────────────────────────────
# 6. CHECK IF FILE EXISTS
# ─────────────────────────────────────────────
def file_exists(filename: str) -> bool:
    """
    Return True if the file exists inside uploads/, False otherwise.

    os.path.exists() checks the filesystem and returns a boolean.
    """
    path = get_safe_path(filename)
    return os.path.exists(path)


# ─────────────────────────────────────────────
# 7. RENAME A FILE
# ─────────────────────────────────────────────
def rename_file(old_filename: str, new_filename: str) -> str:
    """
    Rename a file inside uploads/.

    Both the old and new names are validated to stay inside uploads/.
    os.rename(src, dst) renames src to dst.
    """
    old_path = get_safe_path(old_filename)
    new_path = get_safe_path(new_filename)

    if not os.path.exists(old_path):
        raise FileNotFoundError(f"File '{old_filename}' does not exist.")

    if os.path.exists(new_path):
        raise FileExistsError(f"A file named '{new_filename}' already exists.")

    os.rename(old_path, new_path)

    return f"File renamed from '{old_filename}' to '{new_filename}'."


# ─────────────────────────────────────────────
# 8. COPY A FILE
# ─────────────────────────────────────────────
def copy_file(source_filename: str, destination_filename: str) -> str:
    """
    Copy a file to a new name inside uploads/.

    Both source and destination are validated to stay inside uploads/.
    shutil.copy2() copies the file content and preserves metadata (timestamps).
    """
    source_path = get_safe_path(source_filename)
    destination_path = get_safe_path(destination_filename)

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"File '{source_filename}' does not exist.")

    if os.path.exists(destination_path):
        raise FileExistsError(f"A file named '{destination_filename}' already exists.")

    shutil.copy2(source_path, destination_path)

    return f"File '{source_filename}' copied to '{destination_filename}'."


# ─────────────────────────────────────────────
# 9. DELETE A FILE SAFELY
# ─────────────────────────────────────────────
def delete_file_safe(filename: str) -> str:
    """
    Delete a file from uploads/.

    os.remove() deletes a single file (not a folder).
    We check existence first so the error message is clear.
    """
    path = get_safe_path(filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    os.remove(path)

    return f"File '{filename}' deleted successfully."


# ─────────────────────────────────────────────
# 10. GET FILE SIZE
# ─────────────────────────────────────────────
def get_file_size(filename: str) -> int:
    """
    Return the size of a file in bytes.

    os.path.getsize() returns an integer — the number of bytes in the file.
    For example, a file with the text "Hello" has a size of 5 bytes.
    """
    path = get_safe_path(filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    size_in_bytes = os.path.getsize(path)

    return size_in_bytes
