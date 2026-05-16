Execution of tests:
```bash
docker exec -it lks-fastapi python -m pytest
docker exec -it lks-fastapi python -m pytest --cov=app.services.base --cov-branch --cov-report=term-missing --cov-report=html ./tests/unit/test_base_service.py
```