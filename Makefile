lint:
	ruff check --fix src

formatter:
	isort --profile black src
	black --line-length=120 src