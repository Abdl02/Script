# settings.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
# SQL Server connection string format:
# mssql+pyodbc://<username>:<password>@<host>:<port>/<database>?driver=<driver>
# Replace these values with your actual SQL Server configuration
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "YourStrong@Passw0rd")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "scriptdb")
# Try different driver names that might be available on the system
# Common driver names: "SQL Server", "SQL+Server", "ODBC+Driver+17+for+SQL+Server", "ODBC+Driver+for+SQL+Server"
DB_DRIVER = os.getenv("DB_DRIVER", "SQL+Server")

# Construct the SQLAlchemy database URL
sql_alchemy_database_url = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver={DB_DRIVER}"

# Fallback to SQLite for development/testing if SQL Server connection fails
sqlite_database_url = "sqlite:///./test.db"

# Other settings can be added here
