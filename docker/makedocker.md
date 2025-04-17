## docker_app

### Описание проекта
Данный проект представляет собой приложение на Python, разработанное с использованием Docker на базе Ubuntu 24.04. Приложение включает в себя необходимые зависимости и инструменты, такие как qemu, git, gcc и make.

### Структура
- Makefile             – make-файл для упрощения запуска
- docker-compose.yml   – Файл конфигурации
- Dockerfile           – Основной файл для сборки образа
- .env                 – Файл для переменных окружения

### 1. Cборка контейнера
1) Быть в директории с проектом (`./mse1h2025-xv6` или `./mse1h2025-xv6-main`).
2) Запустить команду:
```bash
make -C docker/ build
```
Для сборки без использования Make
```bash
docker-compose -f docker/docker-compose.yml build
```

### 2. Запуск контейнера
1) Быть в директории с проектом (`./mse1h2025-xv6` или `./mse1h2025-xv6-main`).
2) Запустить команду:
```bash
make -C docker/ run ARGS="<flag> [lab] [archive]"
```
или без Make
```bash
docker-compose -f docker/docker-compose.yml run --rm app <flag> [lab] [archive]
```
где
```
KEYS <flag>:
  --validate [lab] [archive] Загрузить и проверить решение
  --report [lab] [archive]   Показать результаты проверки
PURPUSES:
  [lab] – название лабораторной работы
  [archive] – полное имя загруженного архива
              (путь до него и его имя)

Список названий лабораторных работ:
  util syscall pgtbl traps cow net lock fs mmap

Архив должен быть в формате .zip и содержать один единственный patch-файл, полученный после внесения изменений в клонированный ранее репозиторий xv6-labs-2024 (`git clone git://g.csail.mit.edu/xv6-labs-2024`).
```

### 3. Прекращение работы контейнера
Запустить команду:
```bash
make -C docker/ clean
```
Для прекращения работы не используя Make
```bash
docker-compose -f docker/docker-compose.yml down
```

### Удаление всех остановленных контейнеров
Запустить команду:
```bash
make -C docker/ prune
```
Для удаления контейнеров не используя Make
```bash
docker container prune -f
```
