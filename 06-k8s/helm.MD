## Helm Charts
Документация https://helm.sh/ru/docs/

### Установка Helm Charts
- curl -LO -s https://get.helm.sh/helm-v3.7.0-linux-amd64.tar.gz
- tar -xf helm-v3.7.0-linux-amd64.tar.gz 
- cd linux-amd64/
- sudo mv helm /bin/
- rm -rf linux-amd64/ helm-v3.7.0-linux-amd64.tar.gz
- helm list

### Что такое Helm Charts ?
Helm — это установщик пакетов для Kubernetes. Примерно такой же, как npm для nodejs или apt-get для цивилизованного мира. Говоря helm, мы на самом деле подразумеваем целых два приложения: клиентский helm и его серверного, живущего в Kubernetes компаньона — tiller. На пару они могут искать, устанавливать, апгрэйдить и удалять пакеты-приложения, в хельмовской терминологии называемые чартами (chart).
‘Chart’, установленный в Kubernetes, уже называется релиз (release). Если установить чарт-пакет два раза, то получится два релиза. И т.п.

Helm Charts позволяет легко запускать, обновлять, удалять релизы (версии приложения), а также откатываться на прежние версии.
Он позволяет передавать Gitlab CI/CD variables в кластер и в наше приложение через метки {{ Values.my_value }}.
{{ .Release.Name }} - указание названия релиза

### Структура файлов Helm Charts
Helm Charts имеет структуру:
- Chart.yaml - файл, где указывается описание релиза, параметры
- Папка templates - содержит конфиги k8s, в которые будут ставиться значения из values.yaml
- values.yaml - переменные для templates. Можно указать несколько таких файлов и применять их при релизе

### Основные команды:
Будем считать, что в текущей директории есть папка charts, charts/templates/ и внутри файлы k8s (deployment),
а также файлы charts/Chart.yaml, charts/values.yaml:
- Запуск релиза с названием app `helm install app charts/`
- Просмотр релизов `helm list`
- Можем использовать команды kubectl для просмотра ресурсов k8s (Например, `kubectl get pods`)
- Обновить релиз с указанием переменных helm upgrade app charts/ --set image=ubuntu:latest --set replicaCount=3
- Запуск релиз с указанием файла переменных `helm install app2 charts/ -f prod_values.yaml`
- Создание пакета приложения `helm package charts/`
- Запуск релиза из пакета `helm install app4 App-HelmChart-0.1.0.tgz`
- Удаление релиза `helm delete app1` или `helm uninstall app`