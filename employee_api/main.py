# main.py
# This is the entry point of the entire application.
# The FastAPI app object is created here, and all API routes
# (URL endpoints) will be registered here.

from fastapi import FastAPI, HTTPException
from database import get_connection

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Employee API is running"}


@app.get("/employees")
def get_employees():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()

        return employees

    except Exception as error:
        return {"error": str(error)}

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()


            
@app.get("/employees/search")
def search_employees(keyword: str):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM employees
            WHERE name LIKE %s OR department LIKE %s
        """

        search_value = "%" + keyword + "%"
        cursor.execute(query, (search_value, search_value))

        employees = cursor.fetchall()
        return employees

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to search employees"
        ) from error

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


            
@app.get("/employees/{employee_id}")
def get_employee_by_id(employee_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        query = "SELECT * FROM employees WHERE id = %s"
        cursor.execute(query, (employee_id,))

        employee = cursor.fetchone()

        if employee is None:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        return employee

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve employee"
        ) from error

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

            
@app.post("/employees")
def add_employee(employee: dict):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            INSERT INTO employees (name, email, department, salary)
            VALUES (%s, %s, %s, %s)
        """

        values = (
            employee["name"],
            employee["email"],
            employee["department"],
            employee["salary"]
        )

        cursor.execute(query, values)
        connection.commit()

        return {
            "message": "Employee added successfully",
            "employee_id": cursor.lastrowid
        }

    except KeyError as error:
        raise HTTPException(
            status_code=400,
            detail=f"Missing field: {error}"
        )

    except Exception as error:
        if connection is not None:
            connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to add employee. Check the data and database."
        ) from error

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()

            
@app.put("/employees/{employee_id}")
def update_employee(employee_id: int, employee: dict):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
            UPDATE employees
            SET name = %s, email = %s, department = %s, salary = %s
            WHERE id = %s
        """

        values = (
            employee["name"],
            employee["email"],
            employee["department"],
            employee["salary"],
            employee_id
        )

        cursor.execute(query, values)
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee not found or no changes made"
            )

        return {
            "message": "Employee updated successfully",
            "employee_id": employee_id
        }

    except KeyError as error:
        raise HTTPException(
            status_code=400,
            detail=f"Missing field: {error}"
        )

    except Exception as error:
        if connection is not None:
            connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update employee. Check the data."
        ) from error

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.close()



@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = "DELETE FROM employees WHERE id = %s"
        cursor.execute(query, (employee_id,))
        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        return {
            "message": "Employee deleted successfully",
            "employee_id": employee_id
        }

    except HTTPException:
        raise

    except Exception as error:
        if connection is not None:
            connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete employee"
        ) from error

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()





# ─────────────────────────────────────────────────────────────────
# TEXT FILE OPERATIONS
# All routes work only with files inside the uploads/ folder.
# ─────────────────────────────────────────────────────────────────

from file_operations import (
    create_file,
    write_file,
    append_file,
    read_file_full,
    read_file_lines,
    file_exists,
    rename_file,
    copy_file,
    delete_file_safe,
    get_file_size,
)


# 1. CREATE A FILE
# POST /files/create?filename=notes.txt
@app.post("/files/create")
def api_create_file(filename: str):
    """
    Creates an empty file inside uploads/.
    Fails if the file already exists.
    """
    try:
        message = create_file(filename)
        return {"message": message}

    except FileExistsError as error:
        # 409 Conflict — the resource already exists
        raise HTTPException(status_code=409, detail=str(error))

    except ValueError as error:
        # 400 Bad Request — path tried to escape uploads/
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not create file.")


# 2. WRITE TO A FILE (overwrites)
# POST /files/write?filename=notes.txt
# Body: { "content": "Hello World" }
@app.post("/files/write")
def api_write_file(filename: str, body: dict):
    """
    Writes content to a file, replacing all existing content.
    Send content in the request body as JSON: { "content": "your text" }
    """
    try:
        content = body.get("content", "")
        message = write_file(filename, content)
        return {"message": message}

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not write to file.")


# 3. APPEND TO A FILE
# POST /files/append?filename=notes.txt
# Body: { "content": "New line to add" }
@app.post("/files/append")
def api_append_file(filename: str, body: dict):
    """
    Adds content to the END of a file without removing existing content.
    Send content in the request body as JSON: { "content": "your text" }
    """
    try:
        content = body.get("content", "")
        message = append_file(filename, content)
        return {"message": message}

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not append to file.")


# 4. READ FULL FILE
# GET /files/read?filename=notes.txt
@app.get("/files/read")
def api_read_file(filename: str):
    """
    Returns the entire content of a file as a single string.
    """
    try:
        content = read_file_full(filename)
        return {"filename": filename, "content": content}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not read file.")


# 5. READ FILE LINE BY LINE
# GET /files/read-lines?filename=notes.txt
@app.get("/files/read-lines")
def api_read_file_lines(filename: str):
    """
    Returns each line of a file as a separate item in a list.
    """
    try:
        lines = read_file_lines(filename)
        return {"filename": filename, "lines": lines, "total_lines": len(lines)}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not read file lines.")


# 6. CHECK IF FILE EXISTS
# GET /files/exists?filename=notes.txt
@app.get("/files/exists")
def api_file_exists(filename: str):
    """
    Returns true or false depending on whether the file exists in uploads/.
    """
    try:
        exists = file_exists(filename)
        return {"filename": filename, "exists": exists}

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not check file.")


# 7. RENAME A FILE
# PUT /files/rename?old_filename=notes.txt&new_filename=renamed.txt
@app.put("/files/rename")
def api_rename_file(old_filename: str, new_filename: str):
    """
    Renames a file inside uploads/.
    Both old and new names must stay inside uploads/.
    """
    try:
        message = rename_file(old_filename, new_filename)
        return {"message": message}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not rename file.")


# 8. COPY A FILE
# POST /files/copy?source_filename=notes.txt&destination_filename=backup.txt
@app.post("/files/copy")
def api_copy_file(source_filename: str, destination_filename: str):
    """
    Copies a file to a new name inside uploads/.
    The original file is not removed.
    """
    try:
        message = copy_file(source_filename, destination_filename)
        return {"message": message}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except FileExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not copy file.")


# 9. DELETE A FILE
# DELETE /files/delete?filename=notes.txt
@app.delete("/files/delete")
def api_delete_file(filename: str):
    """
    Deletes a file from uploads/.
    Returns 404 if the file does not exist.
    """
    try:
        message = delete_file_safe(filename)
        return {"message": message}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not delete file.")


# 10. GET FILE SIZE
# GET /files/size?filename=notes.txt
@app.get("/files/size")
def api_get_file_size(filename: str):
    """
    Returns the size of a file in bytes.
    """
    try:
        size = get_file_size(filename)
        return {"filename": filename, "size_in_bytes": size}

    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:
        raise HTTPException(status_code=500, detail="Could not get file size.")
