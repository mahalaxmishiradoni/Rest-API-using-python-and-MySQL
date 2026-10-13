
from database import get_connection

connection = None

try:
    connection = get_connection()
    print("MySQL connection successful!")

except Exception as error:
    print("Connection failed:", error)

finally:
    if connection is not None and connection.is_connected():
        connection.close()
        print("Connection closed.")
