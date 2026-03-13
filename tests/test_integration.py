import requests
import time
import psycopg2

API_URL = "http://localhost:4566/restapis/acxwuw0sqa/dev/_user_request_/orders"

DB_HOST = "localhost"
DB_NAME = "orders_db"
DB_USER = "postgres"
DB_PASSWORD = "postgres"


def test_full_order_flow():

    payload = {
        "product_id": "p100",
        "quantity": 2,
        "user_id": "u200"
    }

    response = requests.post(API_URL, json=payload)

    assert response.status_code == 202

    order_id = response.json()["order_id"]

    time.sleep(5)

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT status FROM orders WHERE id=%s",
        (order_id,)
    )

    result = cursor.fetchone()

    assert result[0] in ["CONFIRMED", "FAILED"]

    cursor.close()
    conn.close()