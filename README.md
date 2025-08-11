# Fanatics Order Allocation API

A Django REST API for allocating orders to distribution centers, simulating a system for Fanatics' e-commerce platform. Built with Python, Django, and Django REST Framework, with optional AWS integration (mocked locally for logging and alerts). The project demonstrates skills in Python, Django, REST APIs, database management, unit testing, and data analysis, tailored to the requirements of a Back-End Developer (Python) role.

## Features
- **Order Allocation**: POST `/allocate/` allocates an order to the nearest distribution center with sufficient stock based on zip code proximity.
- **Data Analysis**: GET `/analytics/` provides metrics per distribution center, including total orders, total quantity, stock remaining percentage, and low stock alerts (<20% of initial stock).
- **Low Stock Alerts**: Generates alerts when a center's stock falls below 20% of its initial stock, saved locally in `alerts/` (mocking AWS CloudWatch Logs).
- **Logging**: Allocation results are saved in `logs/` (mocking AWS S3).
- **Robust Validation**: Input validation via Django REST Framework serializers, preventing invalid orders (e.g., negative quantity, non-numeric zip codes, duplicate order IDs).
- **Authentication**: Basic API Key authentication for all endpoints (header: `Api-Key: your-secret-key`).
- **Unit Tests**: Comprehensive tests covering allocation logic, low stock alerts, and analytics.
- **Database Population**: Custom management command (`populate_centers`) to seed distribution centers, with options to reset or update existing data.

## Project Structure
- `allocation/models.py`: Database models for `Order` and `DistributionCenter`.
- `allocation/views.py`: API logic for order allocation and analytics, with low stock alert generation.
- `allocation/serializers.py`: Input validation for API requests.
- `allocation/tests.py`: Unit tests for allocation, alerts, and analytics.
- `allocation/management/commands/populate_centers.py`: Command to populate or update distribution centers.
- `logs/`: Mock S3 storage for allocation results.
- `alerts/`: Mock CloudWatch storage for low stock alerts.
- `requirements.txt`: Project dependencies.

## CI/CD
- Automated tests run via GitHub Actions: [![Build Status](https://github.com/francisnardi/fanatics/workflows/CI/badge.svg)](https://github.com/francisnardi/fanatics/actions)

## API Documentation
- Access the OpenAPI schema at `/schema/` and interactive docs at `/docs/` after running the server.

## Docker
- Build and run with:
  ```bash
  docker build -t fanatics-api .
  docker run -p 8000:8000 fanatics-api

## Test Coverage
- Run tests with coverage:
  ```bash
  pip install coverage
  coverage run manage.py test
  coverage report

## Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/francisnardi/fanatics-order-allocation.git
   cd fanatics-order-allocation
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. **Apply migrations and populate the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py populate_centers
   ```

4. **Run the server**:
   ```bash
   python manage.py runserver
   ```

5. **Test the API**:
   - Allocate an order (replace `your-secret-key` with the API key defined in `settings.py`):
     ```bash
     curl -X POST http://127.0.0.1:8000/allocate/ -H "Content-Type: application/json" -H "Api-Key: your-secret-key" -d '{"order_id": "O1", "quantity": 10, "zip_code": "10001"}'
     ```
     **Expected output**:
     ```json
     {"order_id": "O1", "center_id": "C1", "status": "allocated"}
     ```
   - Get analytics:
     ```bash
     curl -H "Api-Key: your-secret-key" http://127.0.0.1:8000/analytics/
     ```
     **Expected output** (example):
     ```json
     [
         {"center_id": "C1", "stock": 90, "initial_stock": 100, "remaining_percentage": 90.0, "low_stock_alert": false, "total_orders": 1, "total_quantity": 10},
         {"center_id": "C2", "stock": 50, "initial_stock": 50, "remaining_percentage": 100.0, "low_stock_alert": false, "total_orders": 0, "total_quantity": 0}
     ]
     ```

## Running Tests
Execute unit tests to verify functionality:
```bash
python manage.py test
```

## Comandos de Gestão
- `python manage.py populate_centers`: Populates distribution centers, skipping duplicates.
- `python manage.py populate_centers --reset`: Deletes all centers and repopulates.
- `python manage.py populate_centers --update`: Updates existing centers with new values.

## AWS Integration (Mocked)
- **S3 Mock**: Allocation results are saved in the `logs/` directory, simulating AWS S3 storage.
- **CloudWatch Mock**: Low stock alerts are saved in the `alerts/` directory, simulating AWS CloudWatch Logs.

### Configuração AWS Real
To send alerts to AWS CloudWatch Logs:
1. Install AWS CLI and configure credentials:
   ```bash
   aws configure
   ```
2. Uncomment the `boto3` code in `views.py` and create a log group named `fanatics-alerts` in AWS CloudWatch.
3. Ensure the IAM role has permissions for `logs:PutLogEvents`.

## Notes
- **Context**: Built to simulate a HackerRank challenge for Avenue Code/Fanatics, showcasing skills in Python, Django, REST APIs, and data analysis for an e-commerce sports platform.
- **Database**: Uses SQLite for simplicity; can be adapted for PostgreSQL or AWS RDS for production.
- **Scalability**: Designed with robust validation and error handling, suitable for high-volume order allocation systems.
- **Future Improvements**:
  - Integrate with real AWS services (S3, CloudWatch, SQS).
  - Add pagination and filtering to the `/analytics/` endpoint.
  - Implement advanced authentication (e.g., JWT).
  - Deploy to a cloud platform like AWS Elastic Beanstalk or Heroku.

## Author
Francisco Jose Nardi Filho  
[GitHub](https://github.com/francisnardi) | [LinkedIn](https://linkedin.com/in/francisnardi)