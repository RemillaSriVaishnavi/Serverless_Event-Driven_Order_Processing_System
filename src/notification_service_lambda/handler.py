import json


def lambda_handler(event, context):

    for record in event["Records"]:
        message = json.loads(record["Sns"]["Message"])

        order_id = message["order_id"]
        status = message["new_status"]

        print(f"Order {order_id} status updated to {status}")