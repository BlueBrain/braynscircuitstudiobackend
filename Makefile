test:
	docker-compose run app sh -c "pytest --cov=. --cov-config=.coveragerc --cov-report term-missing --cov-fail-under=70"
