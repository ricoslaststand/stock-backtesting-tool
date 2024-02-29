.PHONY: format-all-files
format-all-files:
	pre-commit run --all-files

.PHONY: server-dev
server-dev:
	uvicorn app.main:app --reload

.PHONY: run-stock-flagging
run-stock-flagging:
	python app/calculate.py
