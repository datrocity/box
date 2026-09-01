.PHONY: setup test cov lint format watch

# Unset any inherited VIRTUAL_ENV so poetry always uses its own managed
# environment for this project, even if the shell has an unrelated venv
# activated (poetry, unlike Hatch, honors an inherited VIRTUAL_ENV).
POETRY := env -u VIRTUAL_ENV -u VIRTUAL_ENV_PROMPT poetry

setup:
	$(POETRY) install

test:
	$(POETRY) run pytest tests

cov:
	$(POETRY) run pytest --cov=box --cov-report=term-missing tests

lint:
	$(POETRY) run ruff check .

format:
	$(POETRY) run ruff format .

watch:
	$(POETRY) run pytest --looponfail tests
