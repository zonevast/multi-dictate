.PHONY: lint check clean test-coverage

check:
	pytest
	./kbd_utils.py
	./wrapping_test_dictate.py

lint:
	./lint.sh

test-coverage:
	pytest test_dictate_unit.py --cov=dictate --cov-report=html --cov-report=term-missing

clean:
	rm -f /tmp/dictate_trigger
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -f .coverage
