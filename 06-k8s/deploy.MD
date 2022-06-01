# Необходимое ПО

Перед тем как управлять нашим контейнеризированным приложением, необходимо установить следующее ПО:

1. [Kubectl](https://kubernetes.io/ru/docs/tasks/tools/install-kubectl/) - инструмент командной строки, который позволяет запускать команды для кластеров Kubernetes
2. [Minikube](https://kubernetes.io/ru/docs/tasks/tools/install-minikube/) - инструмент для запуска одноузлового кластера Kubernetes локально
3. [Lens k8s](https://k8slens.dev/) - IDE для управления кластерами Kubernetes
4. [kubens + kubectx](https://github.com/ahmetb/kubectx) - утилиты для kubectl, которые позволяют просматривать и менять namespace(ns) и context(ctx) кластера
5. [Helm](https://helm.sh/) - менеджер конфигураций Kubernetes, простыми словами надстройка над kubectl, которая помогает простыми командами с помощью шаблонов конфигураций развернуть, обновить или удалить всю инфраструктуру приложения
6. [AWS cli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) - интерфейс командной строки для работы с сервисами AWS

# Этапы деплоя проекта в Kubernetes

1. Локальный деплой (для того, чтобы деплой в облако произошел менее болезненно и более уверенно, необходимо протестировать конфигурацию локально)
2. Деплой проекта в облаке
3. Настройка CI/CD

## Локальный деплой

### Конфигурация кластера

После установки этого ПО давайте взглянем на структуру проекта. Наверняка она выглядит следующим образом:

```
project/
  |- src/
  |  |- api/
  |  |- core/
  |  |- project_name/
  |  |- Dockerfile
  |  |- ...
  |- .gitlab-ci.yml 
  |- docker-compose.yaml
  |- README.md
```

Для написания конфигурации кластера необходимо создать еще одну папку charts на первом уровне вложенности, будет следующая структура:
```
project/
  |- charts/
  |- src/
  |  |- api/
  |  |- core/
  |  |- project_name/
  |  |- Dockerfile
  |  |- ...
  |- .gitlab-ci.yml 
  |- docker-compose.yaml
  |- README.md
```

Структура папки charts должна быть следующая:
```
charts/
 |- templates/
 |   |- autoscaler.yaml
 |   |- configmap.yaml
 |   |- deployment.yaml
 |   |- policy.yaml
 |   |- secret.yaml
 |   |- service.yaml
 |- Chart.yaml
 |- gitlab-admin-service-account.yaml
 |- local_values.yaml
 |- staging_values.yaml
```

Вся конфигурация кластера описывается в файлах .yaml

Описание файлов конфигурации:
1. Chart.yaml - описание чарта, который носит характер описания конфигурации кластера. Также здесь могут указываться зависимости от уже существующих чартов, которые будут использованы в кластере.

Содержание может быть следующим:
```yaml
apiVersion: v2
name: App-HelmChart
description: Helm Chart for <project_name> app
type: application
version: 0.1.0
appVersion: "3.0.0"

keywords:
  - <project_name>
  - http
  - https
```

2. gitlab-admin-service-account.yaml - конфигурация сервисного аккаунта гитлаба, который необходим для скачивания образа приложения

Содержание может быть следующим:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gitlab
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: gitlab-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
  - kind: ServiceAccount
    name: gitlab
    namespace: kube-system
```

3. local_values.yaml и staging_values.yaml - переменные окружения, которые будут использовать в конфигурации, соответственно для локального развертывания и для развертывания в staging окружении. Переменные из этих файлов используются в конфигурации с помощью конструкции {{ .Values.variable }}

Содержание может быть следующим:
```yaml
...
debug: "1"
environment: local
redisHost: redis
redisPort: 6379
...
```

4. templates/autoscaler.yaml - конфигурация autoscaler, который автоматически обновляет ресурс рабочей нагрузки (например, Deployment или StatefulSet) с целью автоматического масштабирования рабочей нагрузки в соответствии со спросом. Эта конфигурация настраивается для под, которые необходимо скейлить

Пример содержания:
```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Values.releasePrefix }}-web-hpa
  namespace: {{ .Values.namespace }}
  labels:
    app: {{ .Values.releasePrefix }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Values.releasePrefix }}-web
  minReplicas: {{ .Values.web.hpa.replica.min | int }}
  maxReplicas: {{ .Values.web.hpa.replica.max | int }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .Values.web.hpa.cpu | int }}
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: {{ .Values.web.hpa.memory | int }}
```

5. templates/configmap.yaml - файл конфигурации с переменными окружения, которые будут прокидыватсья в поды

Пример содержания:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Values.releasePrefix }}-env-variables
  namespace: {{ .Values.namespace }}
data:
  DEBUG: {{ .Values.debug | quote }}
  ENVIRONMENT: {{ .Values.environment }}
  REDIS_HOST: {{ .Values.redisHost }}
  REDIS_PORT: {{ .Values.redisPort | quote }}
  ...
```

6. templates/delpoyment.yaml - конфигурация деплойментов

Пример содержания:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.releasePrefix }}-web
  namespace: {{ .Values.namespace }}
  annotations:
    project: {{ .Values.releasePrefix }}
  labels:
    app: {{ .Values.releasePrefix }}
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 50%
      maxSurge: 25%
  selector:
    matchLabels:
      app: {{ .Values.releasePrefix }}
  template:
    metadata:
      annotations:
        project: {{ .Values.releasePrefix }}
        rollme: {{ randAlphaNum 10 | quote }}
      labels:
        app: {{ .Values.releasePrefix }}
    spec:
      imagePullSecrets:
        - name: {{ .Values.releasePrefix }}-secret-registry
      restartPolicy: Always
      terminationGracePeriodSeconds: 60
      containers:
        - name: {{ .Values.releasePrefix }}-web-container
          image: {{ .Values.image }}
          imagePullPolicy: Always
          resources:
            requests:
              cpu: {{ .Values.web.resources.requests.cpu | quote }}
              memory: {{ .Values.web.resources.requests.memory | quote }}
            limits:
              cpu: {{ .Values.web.resources.limits.cpu | quote }}
              memory: {{ .Values.web.resources.limits.memory | quote }}
          ports:
            - containerPort: {{ .Values.appPort | int }}
          args:
            - daphne
            - smartpunch_app.asgi:application
            - --bind
            - 0.0.0.0
            - --port
            - {{ .Values.appPort | quote }}
            - --proxy-headers
          envFrom:
            - secretRef:
                name: {{ .Values.releasePrefix }}-secret
            - configMapRef:
                name: {{ .Values.releasePrefix }}-env-variables
```

7. templates/policy.yaml - конфигурация правил кластера

Пример содержания:
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ .Values.releasePrefix }}-pdb
  namespace: {{ .Values.namespace }}
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: {{ .Values.releasePrefix }}
```

8. templates/secret.yaml - подобно configmap.yaml, в этом файле указываются переменные окружения с секретным содержанием

Пример содержания:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.releasePrefix }}-secret-registry
  namespace: {{ .Values.namespace }}
data:
  .dockerconfigjson: {{ .Values.gitlabSecret }}
type: kubernetes.io/dockerconfigjson

---
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.releasePrefix }}-secret
  namespace: {{ .Values.namespace }}
data:
  SECRET_KEY: {{ .Values.secretKey | quote | b64enc }}
```

9. templates/service.yaml - конфигурация сервисов

Пример содержания:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.releasePrefix }}-web-service
  namespace: {{ .Values.namespace }}
  annotations:
    project: smurtpunch-app-service
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    service.beta.kubernetes.io/aws-load-balancer-scheme: internet-facing
  labels:
    app: {{ .Values.releasePrefix }}
spec:
  type: ClusterIP
  ports:
    - name: {{ .Values.appPort | quote }}
      protocol: TCP
      port: {{ .Values.appPort | int }}
      targetPort: {{ .Values.appPort | int }}
  selector:
    app: {{ .Values.releasePrefix }}
```

### Запуск кластера

Кластер minikube запускается с помощью следующей команды:
```shell
minikube start
```

После запуска кластера необходимо развернуть проект с помощью конфигураций, описанных в папке charts. Из корня проекта необходимо запустить следующую команду:
```shell
helm upgrade -i <release_name> --namespace <namespace_name> charts/ -f charts/local_values.yaml
```

Для мониторинга запущенных инстансов можно использовать Lens k8s

После того как локальный кластер запускается без ошибок и работает стабильно, можно приступать к деплою приложения в облаке.

Примечание: в локальном кластере может что-то работать не так, как нужно. Причина проблемы может скрываться в том, что кластер развернут в minikube, который может работать не так, как в облаке.
Если причина проблемы не найдена и вы уверены, что проблема появилась из ниоткуда, можно приступать к деплою приложения в облаке

## Деплой проекта в облаке

Для деплоя проекта в облако необходим аккаунт в AWS, конфигурация для kubectl, access key и secret key для конфигурации доступа к сервисам aws. Все это необходимо спросить у тимлида :)

После получения всего вышеперечисленного, необходимо:
1. Вставить конфигурацию для kubectl в файл ~/.kube/config
2. Авторизоваться в интерфейсе командной строки aws cli с помощью полученных ключей и следующей команды:

```shell
aws configure
```

После проделанных действий в Lens k8s появится облачный кластер Kubernetes.
Для деплоя приложения в этот кластер, необходимо создать новый namespace и применить команду helm для развертывания приложения

```shell
kubectl create namespace <namespace_name>
helm upgrade -i <release_name> --namespace <namespace_name> charts/ -f charts/staging_values.yaml
```

После того как вы убедитесь в правильности развертывания приложения, можно переходить к шагу настройки CI/CD

## Настройка CI/CD

Для настройки CI/CD необходимо описать две джобы для раннера:
1. Создание образа приложения
2. Деплой приложения

### Создание образа приложения

Примерное описание джобы для создания образа приложения, может быть следующим:
```yaml
build_staging:
  stage: build
  before_script:
    - docker login -u gitlab-ci-token -p $CI_JOB_TOKEN $CI_REGISTRY
  script:
    - docker build --build-arg CI_COMMIT_SHA=${CI_COMMIT_SHA} --build-arg APNS_CERTIFICATE=${APNS_CERTIFICATE} --build-arg CI_COMMIT_REF_NAME=${CI_COMMIT_REF_NAME} -t ${CI_REGISTRY}/${CI_PROJECT_PATH}/python:${CI_COMMIT_REF_SLUG} -f src/Dockerfile .
    - docker tag ${CI_REGISTRY}/${CI_PROJECT_PATH}/python:${CI_COMMIT_REF_SLUG} ${CI_REGISTRY}/${CI_PROJECT_PATH}/python:latest
    - docker push ${CI_REGISTRY}/${CI_PROJECT_PATH}/python:${CI_COMMIT_REF_SLUG}
  environment:
    name: Staging
  tags:
    - orgenesis
  only:
    - develop
```

### Деплой приложения
```yaml
deploy_staging:
  stage: deploy
  image: git.mircod.com:5050/worktime/backend/k8s-helm:latest
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - echo "$KUBE_CONFIG" > ~/.kube/config
    - chmod 600 ~/.kube/config
    - export C_MESSAGE=$(echo $CI_COMMIT_MESSAGE | tr [:blank:] '_')
    - export R_TAGS=$(echo $CI_RUNNER_TAGS| tr -d [:blank:] | tr ',' ';')
    - export G_USER_NAME=$(echo $GITLAB_USER_NAME | tr [:blank:] '_')
    - export BASE_HELM_VARIABLES="
      --set sqlHost=$SQL_HOST
      --set image=$WEB_IMAGE
      --set sqlPort=$SQL_PORT
      --set sqlDatabase=$SQL_DATABASE
      --set sqlUser=$SQL_USER
      --set sqlPassword=$SQL_PASSWORD
      --set allowedHosts=$ALLOWED_HOSTS
      --set gitlabSecret=$K8S_GITLAB_SECRET
      --set secretKey=$SECRET_KEY
      --set celery.resources.requests.cpu=$CELERY_REQUESTS_CPU
      --set celery.resources.requests.memory=$CELERY_REQUESTS_MEMORY
      --set celery.resources.limits.cpu=$CELERY_LIMITS_CPU
      --set celery.resources.limits.memory=$CELERY_LIMITS_MEMORY
      --set web.hpa.replica.min=$WEB_MIN_REPLICA
      --set web.hpa.replica.max=$WEB_MAX_REPLICA
      --set web.resources.requests.cpu=$WEB_REQUESTS_CPU
      --set web.resources.requests.memory=$WEB_REQUESTS_MEMORY
      --set web.resources.limits.cpu=$WEB_LIMITS_CPU
      --set web.resources.limits.memory=$WEB_LIMITS_MEMORY
      --set celeryBroker=$CELERY_BROKER
      --set emailHost=$EMAIL_HOST
      --set emailPort=$EMAIL_PORT
      --set emailHostPassword=$EMAIL_HOST_PASSWORD
      --set emailHostUser=$EMAIL_HOST_USER
      --set currentSmartPunchDataPipeline=$CURRENT_SMARTPUNCH_DATA_PIPELINE
      --set plantumlServerUrl=$PLANTUML_SERVER_URL
      --set ciCommitMessage=$C_MESSAGE
      --set ciRunnerTags=$R_TAGS
      --set gitlabUserName=$G_USER_NAME
      --set ciCommitTimestamp=$CI_COMMIT_TIMESTAMP
      --set ciProjectUrl=$CI_PROJECT_URL
      --set ciRegistryImage=$CI_REGISTRY_IMAGE
      --set awsAccessKeyId=$AWS_ACCESS_KEY_ID
      --set awsSecretAccessKey=$AWS_SECRET_ACCESS_KEY
      --set awsStorageBucketName=$AWS_STORAGE_BUCKET_NAME
      --set awsS3RegionName=$AWS_S3_REGION_NAME
      "
    - export AWS_ACCESS_KEY_ID=$K8S_AWS_ACCESS_KEY_ID
    - export AWS_SECRET_ACCESS_KEY=$K8S_AWS_SECRET_ACCESS_KEY
    - export AWS_DEFAULT_REGION=$K8S_AWS_DEFAULT_REGION
  tags:
    - aws-eks
  script:
    - export HELM_VARIABLES="
      --set environment=staging
      "
    - echo $BASE_HELM_VARIABLES $HELM_VARIABLES
    - helm dependency update charts/ -n smartpunch-staging
    - helm upgrade -i <release_name> --namespace <namespace_name> charts/ -f charts/staging_values.yaml $BASE_HELM_VARIABLES $HELM_VARIABLES
  environment:
    name: Staging
  only:
    - develop
```

После проделанных действий при каждом пуше в ветку develop будет собираться образ приложения и деплоиться в облаке