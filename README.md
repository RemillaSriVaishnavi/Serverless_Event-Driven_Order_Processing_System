# Serverless Event-Driven Order Processing System

## Project Overview

This project implements a **serverless event-driven backend for an e-commerce order processing system** using AWS services simulated locally with **LocalStack**.

The system demonstrates how modern backend architectures process requests asynchronously using messaging services.

Instead of processing an order immediately, the system places the order in a queue and processes it in the background. This design improves **scalability, reliability, and fault tolerance**.

The architecture uses the following components:

* API Gateway (REST API)
* AWS Lambda functions
* Amazon SQS (message queue)
* Amazon SNS (notifications)
* PostgreSQL database (order storage)
* LocalStack (local AWS service emulation)
* Docker Compose (local environment orchestration)


# Architecture

The system follows an **event-driven architecture**.

Order processing flow:

Client
↓
API Gateway
↓
OrderCreator Lambda
↓
PostgreSQL Database
↓
SQS Queue (OrderProcessingQueue)
↓
OrderProcessor Lambda
↓
SNS Topic (OrderStatusNotifications)
↓
NotificationService Lambda

### Workflow

1. Client sends a `POST /orders` request.
2. API Gateway triggers **OrderCreator Lambda**.
3. OrderCreator:

   * Validates the request
   * Stores order in database
   * Publishes message to SQS.
4. **OrderProcessor Lambda** consumes SQS messages.
5. OrderProcessor:

   * Retrieves order from database
   * Simulates processing
   * Updates order status (`CONFIRMED` or `FAILED`)
   * Publishes notification to SNS.
6. **NotificationService Lambda** receives SNS event and logs the notification.


# Project Structure

```
serverless-order-processing-system

src/
  order_creator_lambda/
    handler.py
    requirements.txt
    Dockerfile

  order_processor_lambda/
    handler.py
    requirements.txt
    Dockerfile

  notification_service_lambda/
    handler.py
    requirements.txt
    Dockerfile

database/
  init.sql

tests/
  test_order_creator.py
  test_integration.py

infrastructure/
  serverless.yml

docker-compose.yml
.env.example
README.md
```


## Local Setup

### 1 Start Docker Services

Start LocalStack and PostgreSQL:

```
docker-compose up -d
```

Verify containers are running:

```
docker ps
```

### 2 Create Database Table

Connect to the database container:

```
docker exec -it postgres psql -U postgres -d orders_db
```

Run:

```
\i /docker-entrypoint-initdb.d/init.sql
```

### 3 Create SQS Queue

```
docker exec -it localstack awslocal sqs create-queue \
--queue-name OrderProcessingQueue
```

Create Dead Letter Queue:

```
docker exec -it localstack awslocal sqs create-queue \
--queue-name OrderProcessingDLQ
```

Verify:

```
docker exec -it localstack awslocal sqs list-queues
```

### 4 Create SNS Topic

```
docker exec -it localstack awslocal sns create-topic \
--name OrderStatusNotifications
```

## API Endpoint

### Create Order

Endpoint:

```
POST /orders
```

Example Request

```
{
 "product_id": "p100",
 "quantity": 2,
 "user_id": "u001"
}
```

Example Response

```
HTTP 202 Accepted
{
 "order_id": "generated-uuid"
}
```

The order will initially have the status:

```
PENDING
```

The background processor will later update the order status.


## Order Status Lifecycle

Order status transitions:

```
PENDING → CONFIRMED
PENDING → FAILED
```

## Running Tests

This project includes **unit tests and integration tests**.

Run tests with:

```
pytest
```

Unit tests verify:

* Input validation
* Lambda logic

Integration tests verify:

* API request processing
* SQS message publishing
* Order processing
* Database updates


## Checking Logs

To view Lambda execution logs:

```
docker logs localstack
```

Expected log example:

```
Order 123 status updated to CONFIRMED
```

## Environment Variables

Environment variables are defined in:

```
.env.example
```

Example variables:

```
DB_HOST=postgres
DB_NAME=orders_db
DB_USER=postgres
DB_PASSWORD=postgres

AWS_ENDPOINT_URL=http://localstack:4566

SQS_QUEUE_URL=http://localstack:4566/000000000000/OrderProcessingQueue
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:000000000000:OrderStatusNotifications
```

## Deployment Template

A basic deployment template is included in:

```
infrastructure/serverless.yml
```

This template demonstrates how the following components would be deployed in AWS:

* Lambda functions
* API Gateway
* SQS queue
* SNS topic

Example deployment using Serverless Framework:

```
serverless deploy
```

## Health Checks

The Docker services include health checks for:

* PostgreSQL
* LocalStack

These ensure services are ready before running tests.

## Key Features

* Event-driven architecture
* Asynchronous order processing
* Message-based communication
* Idempotent processing
* Local AWS environment using LocalStack
* Automated testing
* Docker-based development setup

## Conclusion

This project demonstrates how to build a **scalable and resilient backend system using serverless and event-driven architecture patterns**.

The design decouples system components using message queues and topics, enabling reliable background processing and easier system scaling.
