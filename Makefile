
.PHONY: run dev test fmt
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000
dev:
	uvicorn app.main:app --reload
test:
	pytest -q
fmt:
	python -m black app tests
