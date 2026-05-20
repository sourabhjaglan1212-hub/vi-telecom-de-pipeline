.PHONY: setup kafka-up kafka-down airflow-up airflow-down generate-data run-streaming run-batch dbt-run test clean

setup:
	python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

kafka-up:
	docker compose -f docker/docker-compose.yml up -d zookeeper kafka kafka-ui

kafka-down:
	docker compose -f docker/docker-compose.yml down

airflow-up:
	docker compose -f docker/docker-compose.yml up -d airflow-webserver airflow-scheduler

airflow-down:
	docker compose -f docker/docker-compose.yml stop airflow-webserver airflow-scheduler

generate-data:
	python3 scripts/generate_data.py

run-streaming:
	python3 processing/streaming/cdr_streaming_job.py

run-batch:
	python3 processing/batch/daily_batch_job.py

dbt-run:
	cd dbt_project && dbt run

dbt-test:
	cd dbt_project && dbt test

test:
	pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
