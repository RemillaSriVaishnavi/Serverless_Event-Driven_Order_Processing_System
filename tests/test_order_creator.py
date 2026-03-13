import json
from src.order_creator_lambda.handler import lambda_handler


def test_missing_fields():
    event = {
        "body": json.dumps({
            "product_id": "p1"
        })
    }

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400