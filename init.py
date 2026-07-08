import os
import boto3
import sys
import pymysql


client = boto3.client("ssm", region_name="us-east-2")


def get_param(name):
    return client.get_parameter(
        Name=f"/application/banking/{name}",
        WithDecryption=True
    )["Parameter"]["Value"]


conn = None

try:
    conn = pymysql.connect(
        host=get_param("DB_HOST"),
        port=int(get_param("DB_PORT")),
        user=get_param("DB_USER"),
        password=get_param("DB_PASSWORD"),
        connect_timeout=10,
        autocommit=True
    )

    cur = conn.cursor()

    with open("/tmp/init.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cur.execute(statement)

    print("✅ Database initialized successfully")

except Exception as e:
    print(f"❌ Error: {e}")
    raise

finally:
    if conn:
        conn.close()