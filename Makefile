db-clean:
	python3 ./scripts/database.py
	python3 ./scripts/flyway.py clean

db-migrate:
	python3 ./scripts/database.py
	python3 ./scripts/flyway.py migrate

docker-down:
	docker-compose down --volumes

docker-up:
	docker-compose build --no-cache
	docker-compose up -d

run:
	./setup.sh

test:
	make db-migrate
	export PYTHONPATH=$(pwd) 
	pytest -v