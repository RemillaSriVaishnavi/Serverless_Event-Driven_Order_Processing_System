import json
import os
import time
import random
import boto3
import psycopg2

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "orders_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")

sns = boto3.client(
    "sns",
    endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566"),
    region_name="us-east-1",
    aws_access_key_id="test",
    aws_secret_access_key="test"
)


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def lambda_handler(event, context):

    for record in event["Records"]:
        body = json.loads(record["body"])
        order_id = body["order_id"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Idempotency check
        cursor.execute(
            "SELECT status FROM orders WHERE id=%s",
            (order_id,)
        )

        result = cursor.fetchone()

        if not result:
            print("Order not found")
            continue

        status = result[0]

        if status != "PENDING":
            print("Order already processed")
            continue

        # Simulate processing
        time.sleep(2)

        new_status = random.choice(["CONFIRMED", "FAILED"])

        cursor.execute(
            "UPDATE orders SET status=%s, updated_at=NOW() WHERE id=%s",
            (new_status, order_id)
        )

        conn.commit()

        cursor.close()
        conn.close()

        message = {
            "order_id": order_id,
            "new_status": new_status
        }

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message)
        )

        print(f"Order {order_id} updated to {new_status}")