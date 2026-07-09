install:
	pip install -r requirements.txt

test:
	pytest

format:
	black .

lint:
	ruff check .

run:
	streamlit run app.py