.PHONY: help install run train evaluate test docker-build docker-run clean

PYTHON := python3

help:
	@echo "NeuroVision AI - Command Suite"
	@echo "--------------------------------"
	@echo "make install      : Install all dependencies from requirements.txt"
	@echo "make run          : Start the Flask application locally"
	@echo "make train        : Execute the transfer learning & fine-tuning pipeline"
	@echo "make evaluate     : Evaluate model and generate confusion matrix & ROC"
	@echo "make test         : Run automated test suite with pytest"
	@echo "make docker-build : Build Docker container image"
	@echo "make docker-run   : Run application in Docker container"
	@echo "make clean        : Remove temporary cache, uploads and artifacts"

install:
	pip install -r requirements.txt

run:
	$(PYTHON) app.py

train:
	$(PYTHON) src/train.py

evaluate:
	$(PYTHON) src/evaluate.py

test:
	pytest tests/ -v

docker-build:
	docker build -t neurovision-ai:latest .

docker-run:
	docker run -p 5000:5000 neurovision-ai:latest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage
