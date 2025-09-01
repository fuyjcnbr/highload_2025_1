

## Сборка контейнера

```console
foo@bar:~$ docker build --no-cache --squash -t highload_hw_1 -f Dockerfile .
```

## Запуск контейнера

```console
foo@bar:~$ docker run -v ~/PycharmProjects/highload_2025_1:/src -p 8223:8223 -p 5832:5432 -it highload_hw_1 /bin/bash
```


## Тестовая база

5832 test_db  root/root


## Примеры запросов к http api

### register

http://127.0.0.1:8223/user/register

{
  "username": "user1",
  "password": "pass1",
  "name": "lala"
}


### login

http://127.0.0.1:8223/login

{
  "username": "user1",
  "password": "pass1"
}


### get

http://127.0.0.1:8223/user/get/<token>



