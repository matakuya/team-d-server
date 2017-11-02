## mysql.iniの作成

```ini:mysql.ini
[connect]
host = localhost
user = root
passwd = YOUR_MYSQL_PASSWORD
db = YOUR_BATADASE_NAME
charset = utf8
```

## テーブルの作成

`create table log(id int auto_increment not null primary key, user_id int, temp int, hot_cold int, created_at datetime not null default current_timestamp);
`

## 必要なパッケージのインストール
`$ pip3 install -r requirements.txt`

## 起動
`$ python3 main.py`