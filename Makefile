.PHONY: setup test cov lint format watch

setup:
	hatch env create

test:
	hatch run test

cov:
	hatch run cov

lint:
	hatch run lint

format:
	hatch run format

watch:
	hatch run pytest --looponfail tests
