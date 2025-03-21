# Сборка Docker-образа и запуск контейнера
build:
	docker-compose -f docker-compose.yml build
    
# Запуск контейнера
run:
	docker-compose -f docker-compose.yml run --rm app $(ARGS)

# Остановка и удаление контейнера
clean:
	docker-compose down

# Удаление всех остановленных контейнеров
prune:
	docker container prune -f

