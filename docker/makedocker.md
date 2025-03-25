# docker_app

## Описание проекта
Данный проект представляет собой приложение на Python, разработанное с использованием Docker на базе Ubuntu 24.04. Приложение включает в себя необходимые зависимости и инструменты, такие как qemu, git, gcc и make.

## Структура
docker-compose.yml     - Файл конфигурации
   
Dockerfile             - Основной файл для сборки образа
   
requirements.txt       - Файл для установки зависимостей
   
script.sh              - Запускаемый скрипт
   
.env                   - Файл для переменных окружения

## Cборка контейнера
1. Перейти в необходимый каталог
2. Запустить команду:
```bash
make -C docker/ build
```
Для сборки без использования Make
```bash
docker-compose -f docker/docker-compose.yml build
```
## Запуск контейнера
1. Перейти в необходимый каталог
2. Запустить команду:
```bash
make -C docker/ run ARGS="<flag> <lab> <ARCHIVE>"
```
или без Make
```bash
docker-compose -f docker/docker-compose.yml run --rm app <flag> <lab> <ARCHIVE>
```
где   [LAB] - название лабораторной работы, [ARCHIVE] - полный путь до загруженного архива в контейнере(app/solution). Архив должен быть в формате  .zip <br>
Список названий лабораторных работ:<br>
  util syscall pgtbl traps cow net lock fs mmap<br>
  
Для корректной работы архив должен находится в папке solution/
## Прекращение работы контейнера
Запустить команду:
```bash
make -C docker/ clean
```
Для прекращения работы не используя Make
```bash
docker-compose -f docker/docker-compose.yml down
```

## Удаление всех остановленных контейнеров
Запустить команду:
```bash
make -C docker/ prune
```
Для удаления контейнеров не используя Make
```bash
docker container prune -f
```


