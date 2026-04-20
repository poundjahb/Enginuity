.PHONY: dev down logs backend-test-analyst backend-test

dev:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

backend-test-analyst:
	cd services/backend && pytest -q tests/test_analyst_validation.py

backend-test:
	cd services/backend && pytest -q tests
