.PHONY: up down logs clean init

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v
	rm -rf data/

init:
	mkdir -p data/qdrant data/neo4j data/langfuse
