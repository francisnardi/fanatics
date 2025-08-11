# Fanatics Order Allocation API

A Django REST API for allocating orders to distribution centers, simulating a system for Fanatics' e-commerce platform. Built with Python, Django, and Django REST Framework, with optional AWS S3 integration (mocked locally).

## Features
- POST `/allocate/`: Allocates an order to the nearest distribution center with sufficient stock.
- GET `/analytics/`: Returns order allocation analytics per distribution center.
- Mock S3 logging to store allocation results.
- Unit tests included.