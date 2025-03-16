.PHONY: run
run:
	uv run --env-file .env python -m oura_bot.main

.PHONY: help
help:
	@echo "run        - Run the bot"
