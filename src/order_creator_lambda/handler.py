import json
import uuid
import os
import boto3
import psycopg2

# Environment variables
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_NAME = os.getenv("DB_NAME", "orders_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")

sqs = boto3.client(
    "sqs",
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

    try:
        body = json.loads(event.get("body", "{}"))

        product_id = body.get("product_id")
        quantity = body.get("quantity")
        user_id = body.get("user_id")

        if not product_id or not quantity or not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields"})
            }

        order_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO orders (id, user_id, product_id, quantity, status)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            insert_query,
            (order_id, user_id, product_id, quantity, "PENDING")
        )

        conn.commit()

        cursor.close()
        conn.close()

        # Send message to SQS
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({"order_id": order_id})
        )

        return {
            "statusCode": 202,
            "body": json.dumps({"order_id": order_id})
        }

    except Exception as e:
        print(str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }