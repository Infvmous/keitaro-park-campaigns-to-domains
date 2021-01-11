1. Создать файл `run.sh` и записать в него

```bash
export API_KEY='KEITARO ADMIN API KEY'
export HOST='URL TO KEITARO'
python . $1
```

2. Загрузить в директорию со скриптом \*.csv файл со списком имен кампаний и доменов (пример см. в файле `example.csv`)

3. В терминале запустить скрипт `run.sh`

```bash
$ source run.sh имя_csv_файла
```
