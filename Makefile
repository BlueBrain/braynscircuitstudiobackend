migrate:
	docker-compose run bcsb sh -c "python apps/bcsb/manage.py migrate"

migrations:
	docker-compose run bcsb sh -c "python apps/bcsb/manage.py makemigrations"

superuser:
	docker-compose run bcsb sh -c "python apps/bcsb/manage.py createsuperuser"

changepassword:
	docker-compose run bcsb sh -c "python apps/bcsb/manage.py changepassword $(username)"

test:
	docker-compose run bcsb sh -c "pytest --cov=. --cov-config=.coveragerc --cov-report term-missing --cov-fail-under=70"
