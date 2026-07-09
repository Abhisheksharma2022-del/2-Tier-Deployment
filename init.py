import boto3
import pymysql

REGION = "us-east-2"
PARAMETER_PATH = "/application/banking"

client = boto3.client("ssm", region_name=REGION)


def get_param(name):
    return client.get_parameter(
        Name=f"{PARAMETER_PATH}/{name}",
        WithDecryption=True
    )["Parameter"]["Value"]


conn = None

try:
    print("Fetching database parameters from SSM...")

    DB_HOST = get_param("DB_HOST")
    DB_PORT = int(get_param("DB_PORT"))
    DB_USER = get_param("DB_USER")
    DB_PASSWORD = get_param("DB_PASSWORD")

    print(f"Connecting to MySQL server: {DB_HOST}:{DB_PORT}")

    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10,
        autocommit=True
    )

    cursor = conn.cursor()

    print("Executing init.sql...")

    with open("/tmp/init.sql", "r", encoding="utf-8") as file:
        sql = file.read()

    statements = sql.split(";")

    for statement in statements:
        statement = statement.strip()
        if statement:
            cursor.execute(statement)

    cursor.close()

    print("Database initialized successfully.")

except pymysql.MySQLError as e:
    print(f"MySQL Error: {e}")
    raise

except Exception as e:
    print(f"Unexpected Error: {e}")
    raise

finally:
    if conn:
        conn.close()
        print("Database connection closed.")