# Run all tests
.PHONY: test
test:
	pytest tests --log-cli-level=info --disable-warnings


.PHONY: build-airflow-image
build-airflow-image:
	docker build \
	--build-arg airflow_ver=2.0.1 \
	--build-arg python_ver=3.8 \
	-t koorosh/airflow:2.0.1 \
	-f ./cluster/images/airflow/Dockerfile ./cluster/images/airflow