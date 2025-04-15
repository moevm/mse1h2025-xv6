<div align="justify">

# Автоматизация новых версий задачника XV6

# Wiki

[Home](https://github.com/moevm/mse1h2025-xv6/wiki) page:
- [Краткое описание проекта](https://github.com/moevm/mse1h2025-xv6/wiki#%D0%BA%D1%80%D0%B0%D1%82%D0%BA%D0%BE%D0%B5-%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
- [Цель проекта](https://github.com/moevm/mse1h2025-xv6/wiki#%D1%86%D0%B5%D0%BB%D1%8C-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
- [Задачи проекта](https://github.com/moevm/mse1h2025-xv6/wiki#%D0%B7%D0%B0%D0%B4%D0%B0%D1%87%D0%B8-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82%D0%B0)
- [Описание основной проблемы, которую решает проект](https://github.com/moevm/mse1h2025-xv6/wiki#%D0%BE%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE%D0%B9-%D0%BF%D1%80%D0%BE%D0%B1%D0%BB%D0%B5%D0%BC%D1%8B-%D0%BA%D0%BE%D1%82%D0%BE%D1%80%D1%83%D1%8E-%D1%80%D0%B5%D1%88%D0%B0%D0%B5%D1%82-%D0%BF%D1%80%D0%BE%D0%B5%D0%BA%D1%82)
- [Список функциональных и нефункциональных требований](https://github.com/moevm/mse1h2025-xv6/wiki#%D1%81%D0%BF%D0%B8%D1%81%D0%BE%D0%BA-%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D1%85-%D0%B8-%D0%BD%D0%B5%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D0%BE%D0%BD%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D1%85-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D0%B9)
- [Категории пользователей](https://github.com/moevm/mse1h2025-xv6/wiki#%D0%BA%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D0%B8-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D0%B5%D0%B9)
- [Сценарии использования](https://github.com/moevm/mse1h2025-xv6/wiki#%D1%81%D1%86%D0%B5%D0%BD%D0%B0%D1%80%D0%B8%D0%B8-%D0%B8%D1%81%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F)
- [Макет UI](https://github.com/moevm/mse1h2025-xv6/wiki#%D0%BC%D0%B0%D0%BA%D0%B5%D1%82-ui)

[Запуск лабораторных работ и фиксация результатов](https://github.com/moevm/mse1h2025-xv6/wiki/%D0%97%D0%B0%D0%BF%D1%83%D1%81%D0%BA-%D0%BB%D0%B0%D0%B1%D0%BE%D1%80%D0%B0%D1%82%D0%BE%D1%80%D0%BD%D1%8B%D1%85-%D1%80%D0%B0%D0%B1%D0%BE%D1%82-%D0%B8-%D1%84%D0%B8%D0%BA%D1%81%D0%B0%D1%86%D0%B8%D1%8F-%D1%80%D0%B5%D0%B7%D1%83%D0%BB%D1%8C%D1%82%D0%B0%D1%82%D0%BE%D0%B2)

# Инструкция

## Условные обозначения

Для избежания недопониманий необходимо принять следующие условные обозначения для дирректорий:
- BASE_DIR – директория с проектом:
    * `./mse1h2025-xv6` – если в текущую директорию `./` склонирован репозиторий проекта с помощью `git clone https://github.com/moevm/mse1h2025-xv6.git`;
    * `./mse1h2025-xv6-main` – если в текущую директорию `./` скачена зипка проекта `./mse1h2025-xv6-main.zip`, а зачем разорхивирована в текущую директорию `./`;
- SCRIPTS_DIR=`"$BASE_DIR/scripts"` – директория с кодом проекта (кодом, реализующим автоматизацию новых версий задачника XV6);
- SOLUTION_DIR=`"$BASE_DIR/solution"` – директория, предназначенная для хранения архива/архивов с решением;
- LOGS_DIR=`"$BASE_DIR/logs"` – директория, куда сохраняются все логи (файлы `"$LOGS_DIR/load.log"`, `"$LOGS_DIR/file_checker.log"`, `"$LOGS_DIR/qemu-gdb.log"`, `"$LOGS_DIR/error.log"` и финальный объединяющий все предыдущие log_file);
- RESULTS_DIR=`"$LOGS_DIR"` – директория, куда сохраняется report_file (совпадает с LOGS_DIR);

а также:
- archive – полное имя загружаемого архива (путь к архиву + имя архива);
- archive_name – имя архива;
- log_file=`"$LOGS_DIR/$archive_name.log"` – лог-файл, объединяющий все логи (логи загрузки, тривиальных проверок, запуска проверок выполненной лабораторной работы и логи ошибок) в один лог-файл;
- report_file=`"$RESULTS_DIR/$archive_name.json"` – файл формата .json, созданный из логов log_file.

## I. Выполнение лабораторной работы

### 1. Установка системы
Установить и протестировать систему "6.1810: Operating System Engineering" по инструкции [Tools Used in 6.1810](https://pdos.csail.mit.edu/6.828/2024/tools.html).

### 2. Загрузка репозитория с лабораторными работами
Как сказано в инструкции к [первой лаборатороной работе](https://pdos.csail.mit.edu/6.828/2024/labs/util.html), необходимо клонировать оригинальный репозиторий с лабораторными работами с помощью команды:
```bash
git clone git://g.csail.mit.edu/xv6-labs-2024
```
и перейти в склонированный репозиторий с помощью команды:
```bash
cd xv6-labs-2024
```

### 3. Собственно выполнение лабораторной работы
Перейти в ветку с лабораторной работой, которую нужно выполнить, с помощью команды: `git checkout _название_лабы_`
1. `git checkout util`
2. `git checkout syscall`
3. `git checkout pgtbl`
4. `git checkout traps`
5. `git checkout cow`
6. `git checkout net`
7. `git checkout lock`
8. `git checkout fs`
9. `git checkout mmap`

Выполнить соответствующую лабораторную работу:
1. [Lab: Xv6 and Unix utilities](https://pdos.csail.mit.edu/6.828/2024/labs/util.html)
2. [Lab: system calls](https://pdos.csail.mit.edu/6.828/2024/labs/syscall.html)
3. [Lab: page tables](https://pdos.csail.mit.edu/6.828/2024/labs/pgtbl.html)
4. [Lab: traps](https://pdos.csail.mit.edu/6.828/2024/labs/traps.html)
5. [Lab: Copy-on-Write Fork for xv6](https://pdos.csail.mit.edu/6.828/2024/labs/cow.html)
6. [Lab: networking](https://pdos.csail.mit.edu/6.828/2024/labs/net.html)
7. [Lab: locks](https://pdos.csail.mit.edu/6.828/2024/labs/lock.html)
8. [Lab: file system](https://pdos.csail.mit.edu/6.828/2024/labs/fs.html)
9. [Lab: mmap](https://pdos.csail.mit.edu/6.828/2024/labs/mmap.html)

## II. Создание архива с решением

После создания и изменения всех файлов, которые потребовалось создать и изменить для выполнения выбранной лабораторной работы, необходимо сохранить решение в виде patch-файла.

### Создание patch-файла
1) Добавить созданные и изменённые файлы в индекс с помощью команды:
```bash
git add *
```
2) Создать patch-файл с помощью команды:
```bash
git diff origin/_название_лабы_ > _название_patch-файла_.patch
```

### Архивирование решения
Необходимо архивировать полученный patch-файл в архив формата .zip. </br>
И пусть `_название_patch-файла_` == имени архива.

В SOLUTION_DIR лежат два примера архива с решением (patch-файлом) внутри: `"$BASE_DIR/solution/util_110of110_git_diff.zip` и `"$BASE_DIR/solution/0001-util_110of110_git_format-patch.zip`.

**I и II шаг для преподавателя** – получить архив/архивы с решением от студента/студентов.

## III. Загрузка архива с решением

1) Загрузить репозиторий проекта "mse1h2025-xv6":
    * склонировать репозиторий проекта с помощью команды `git clone https://github.com/moevm/mse1h2025-xv6.git`
    * или скачать зипку проекта `./mse1h2025-xv6-main.zip`, разорхивировать её в текущую директорию `./`.
2) Перейти в BASE_DIR:
    * перейти в склонированный `./mse1h2025-xv6` командой `cd ./mse1h2025-xv6`
    * или соответсвенно перейти в полученную дирректорию `./mse1h2025-xv6-main` командой `cd ./mse1h2025-xv6-main`.
3) Скопировать/переместить (на усмотрение пользователя) архив с решением в SOLUTION_DIR.

## IV. Запуск системы с помощью Docker

### 1. Cборка контейнера
1) Быть в BASE_DIR.
2) Запустить команду:
```bash
make -C docker/ build
```
Для сборки без использования Make
```bash
docker-compose -f docker/docker-compose.yml build
```

### 2. Запуск контейнера
1) Быть в BASE_DIR.
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

## Получаемый результат

- После запуска контейнера с флагом `--validate` система сгенерирует log_file=`"$LOGS_DIR/$archive_name.log"` и report_file=`"$RESULTS_DIR/$archive_name.json"`. log_file находится LOGS_DIR=`"$BASE_DIR/logs"`, report_file находится в RESULTS_DIR=`"$LOGS_DIR"` (из соображений избыточности они совпадают).
- После запуска контейнера с флагом `--report` log_file выводится на экран.
