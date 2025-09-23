.PHONY: lint format check install clean

lint:
	sed -i 's/[[:space:]]*$$//' dictate.py
	-flake8 dictate.py --max-line-length=120 --ignore=E203,W503,W504
	black dictate.py --line-length=120

clean:
	rm -f /tmp/dictate_trigger
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
