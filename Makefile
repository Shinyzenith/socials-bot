all: run

run:
	@python3 ./src/bot.py

clean:
	@rm -rf **/**/__pycache__
	@rm -rf **/__pycache__
	@rm -rf .tox

clean_db: clean
	@rm -f *.db

lint:
	@tox

.PHONY: clean lint run clean_db
