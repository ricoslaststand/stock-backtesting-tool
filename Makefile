format-all-files:
	pre-commit run --all-files

server-dev:
	uvicorn app.main:app --reload
