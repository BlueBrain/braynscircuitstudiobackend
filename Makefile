migrate:
	docker-compose run app sh -c "python braynscircuitstudiobackend/manage.py migrate"

migrations:
	docker-compose run app sh -c "python braynscircuitstudiobackend/manage.py makemigrations"

changepassword:
	docker-compose run app sh -c "python braynscircuitstudiobackend/manage.py changepassword $(username)"

test:
	docker-compose run app sh -c "pytest --cov=. --cov-config=.coveragerc --cov-report term-missing --cov-fail-under=80"
