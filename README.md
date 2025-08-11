# Fanatics Order Allocation API

[![Build Status](https://github.com/francisnardi/fanatics/workflows/CI/badge.svg)](https://github.com/francisnardi/fanatics/actions)
[![codecov](https://codecov.io/gh/francisnardi/fanatics/branch/main/graph/badge.svg)](https://codecov.io/gh/francisnardi/fanatics)

A Django REST API for e-commerce order allocation, simulating Fanatics' order management system. The API allocates orders to distribution centers based on stock availability and zip code proximity, provides analytics on stock levels, and generates low-stock alerts with AWS-compatible logging (mocked locally). Built with Python, Django, and Django REST Framework, it includes robust input validation, unit tests (~85% coverage), and CI/CD integration via GitHub Actions and Codecov.

## Features
- **Order Allocation (`/allocate/`)**: Assigns orders to the nearest distribution center with sufficient stock, updating inventory and logging results (mock S3).
- **Analytics Endpoint (`/analytics/`)**: Provides metrics like remaining stock percentage, total orders, and low-stock alerts (<20% of initial stock).
- **Low Stock Alerts**: Logs alerts to `alerts/` (mock CloudWatch) when stock falls below 20% of initial levels.
- **Input Validation**: Ensures positive quantities, numeric zip codes, and unique order IDs.
- **Authentication**: Secures endpoints with API Key authentication.
- **Data Population**: Custom Django command (`populate_centers`) with `--reset` and `--update` options to manage distribution center data.
- **API Documentation**: Interactive OpenAPI schema at `/schema/` and Swagger UI at `/docs/` (via `drf-spectacular`).
- **Testing**: ~85% test coverage with unit tests for allocation, validation, analytics, and authentication.
- **CI/CD**: Automated testing and coverage reporting via GitHub Actions and Codecov.

## Prerequisites
- Python 3.10+
- pip
- Virtualenv (recommended)
- Git

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/francisnardi/fanatics.git
   cd fanatics
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Populate Distribution Centers**:
   ```bash
   python manage.py populate_centers
   ```
   - Use `--reset` to clear and repopulate data.
   - Use `--update` to update existing centers.

6. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access Endpoints**:
   - Allocate an order:
     ```bash
     curl -X POST http://127.0.0.1:8000/allocate/ -H "Content-Type: application/json" -H "Api-Key: your-secret-key" -d '{"order_id": "O1", "quantity": 10, "zip_code": "10001"}'
     ```
   - View analytics:
     ```bash
     curl http://127.0.0.1:8000/analytics/ -H "Api-Key: your-secret-key"
     ```
   - Explore API docs: `http://127.0.0.1:8000/docs/` (requires API Key).

## Test Coverage
- Run tests with coverage:
  ```bash
  pip install pytest pytest-cov
  pytest --cov=. --cov-branch --cov-report=xml
  ```
- Current coverage: ~85% (covering models, serializers, views, and commands).
- Coverage report: [![codecov](https://codecov.io/gh/francisnardi/fanatics/branch/main/graph/badge.svg)](https://codecov.io/gh/francisnardi/fanatics)

## AWS Integration (Mock)
- **S3 Mock**: Order allocation results are saved as JSON in `logs/`.
- **CloudWatch Mock**: Low-stock alerts are saved as JSON in `alerts/`.
- **Real AWS Setup**:
  1. Configure AWS credentials with `aws configure`.
  2. Uncomment `boto3` code in `allocation/views.py` to use real S3/CloudWatch.
  3. Create a CloudWatch log group (`fanatics-alerts`) and S3 bucket.

## Troubleshooting GitHub Actions
- If Actions fails, check logs at `/actions` for dependency or migration issues.
- Ensure `logs/` and `alerts/` directories are created in CI with `mkdir -p logs alerts`.
- Verify `requirements.txt` includes `django`, `djangorestframework`, `boto3`, `drf-spectacular`, `pytest`, `pytest-cov`.

## Project Structure
```
fanatics/
├── allocation/
│   ├── models.py           # Models for DistributionCenter and Order
│   ├── views.py           # API endpoints for allocation and analytics
│   ├── serializers.py      # Input validation for orders
│   ├── tests.py           # Unit tests (~85% coverage)
│   ├── management/
│   │   └── commands/
│   │       └── populate_centers.py  # Custom command to populate data
├── logs/                  # Mock S3 storage for order logs
├── alerts/                # Mock CloudWatch storage for low-stock alerts
├── order_allocation/
│   ├── settings.py        # Django settings with DRF and drf-spectacular
│   ├── urls.py            # API routes including OpenAPI schema
├── requirements.txt       # Dependencies
├── .github/workflows/ci.yml  # GitHub Actions for CI/CD
├── README.md              # This file
```

## Development Notes
- **Authentication**: Set `API_KEY` in environment variables for production (default: `your-secret-key` for development).
- **Performance**: Analytics endpoint uses Django ORM for aggregations; consider caching for large datasets.
- **Future Improvements**:
  - Add pagination to `/analytics/`.
  - Implement real AWS S3/CloudWatch integration.
  - Add more advanced analytics (e.g., order trends over time).

## Contributing
Feel free to open issues or PRs for bug fixes or enhancements. Run tests before submitting changes:
```bash
pytest --cov=. --cov-report=xml
```

## License
This project is unlicensed for demonstration purposes. For production use, contact the author.

---

Built by [Francisco Nardi](https://github.com/francisnardi) as a technical challenge for Fanatics/Avenue Code.