# Развёртывание приложения в Kubernetes

Приложение запускается в контейнере на порту `8000`. Для доступа к приложению внутри кластера был создан Service, который проксирует входящий трафик с порта `80` на порт `8000` контейнера и выполняет балансировку нагрузки между pod’ами.

Я выбрал способ `HostPort` + `DNS`, в качестве DNS выступает [Tailscale](https://tailscale.com/), который позволяет пробрасывать наружу свой сервис и автоматически подключает сертификаты для доступа по  HTTPS. Tailscale выдает DNS адрес из своей сети (tailnet), к которому можно подключится из любой точки мира. Tailscale ставиться на сервер и после авторизации создается туннель, через который можно пробросить порт и подключаться к нему через публичный DNS адрес.

## Архитектура
Интернет → Tailscale Funnel → master → Ingress → Service → Pods (worker1, worker2)

## Компоненты
- Deployment (2 реплики)
- Service (порт 80 → 8000)
- Ingress (NGINX)
- Ingress Controller (DaemonSet + hostNetwork)
- Tailscale Funnel (HTTPS)

Было создано 2 реплики для обеспечения отказоустойчивости, которые располагаются на разных нодах. Ingress Controller был развернут в виде DaemonSet и настроен с использованием hostNetwork, для обеспечения возможности принимать трафик непосредственно на нодах кластера через стандартные порты 80 и 443.

## Доступ
https://currency-service.tailaaac65.ts.net/info

## Отказоустойчивость
- 2 реплики
- разные worker-ноды
- балансировка через Service
- автоперезапуск pod

## Балансировка
Ingress → Service → Pods (round-robin)

## Проблема и решение
- Calico использовал интерфейс tailscale0 → сеть не работала

    Решение:
    ```
    kubectl set env daemonset/calico-node -n kube-system IP_AUTODETECTION_METHOD=cidr=10.184.0.0/24
    ```

- Реплики создавались на одной и той же ноде.

    Решение:
    Оказалось что на второй ноде закончилась память, было очищено 2.5 ГБ удалением всего неиспользуемого в Docker
    ```
    docker system prune -a
    ```



# CI/CD и GitOps

Для автоматизации сборки и доставки приложения был настроен CI/CD с использованием ArgoCD и ArgoCD Image Updater.

## Архитектура CI/CD

Git push → Jenkins → DockerHub → Docker build → Secure Tests → ArgoCD Image Updater → ArgoCD → Kubernetes

## Jenkins

Jenkins используется для CI. Pipeline автоматически выполняет:

- linting Dockerfile и Python-кода
- запуск тестов
- публикацию image в DockerHub
- сборку Docker image
- smoke tests
- security-сканирование image
- SAST-анализ

При создании git tag вида `v1.0`, `v1.2.3` автоматически формируется production-сборка.

## DockerHub

DockerHub используется как registry для хранения Docker image.

Используются разные типы тегов:
- `latest` — staging
- `v1`, `v1.2`, `v1.2.3` — production

## ArgoCD

Для CD  был выбран ArgoCD. Он реализует GitOps-подход, при котором состояние кластера описывается в Git-репозитории.

ArgoCD автоматически:
- отслеживает изменения в Git
- синхронизирует Kubernetes cluster с репозиторием
- выполняет rollout новой версии

## Helm

Для управления Kubernetes manifests был использован Helm chart.

Это позволило:
- разделить staging и production окружения
- использовать разные values-файлы
- удобно управлять image tags
- параметризовать Service и Ingress

Структура chart:

```
├── currency-service
│   ├── Chart.yaml
│   ├── templates
│   │   ├── deployment.yaml
│   │   ├── ingress.yaml
│   │   └── service.yaml
│   ├── values-prod.yaml
│   ├── values-stage.yaml
│   └── values.yaml
```

## Разделение stage и prod

Были созданы два отдельных namespace:
- `currency-service-stage`
- `currency-service-prod`

Для каждого окружения используется отдельный ArgoCD Application и отдельный values-файл Helm.

Особенности:
- stage автоматически обновляется при публикации новых latest image
- production обновляется только для release tags вида `v1`, `v1.2.3`
- production запущен на порту 80
- stage через NodePort на 30080

Для production была настроена фильтрация тегов через regexp:

```
regexp:^v[0-9]+(\.[0-9]+)*$
```

## ArgoCD Image Updater

ArgoCD Image Updater автоматически отслеживает появление новых Docker image в DockerHub и обновляет Kubernetes deployment без ручного запуска `kubectl apply`.

После публикации нового image происходит:
1. обнаружение нового тега
2. обновление Helm parameters
3. автоматический sync ArgoCD
4. rollout новой версии приложения

## Почему был выбран ArgoCD

ArgoCD был выбран потому что:
- реализует GitOps-подход
- имеет удобный web UI
- автоматически синхронизирует cluster state
- поддерживает rollback
- хорошо интегрируется с Helm
- позволяет разделять CI и CD
- поддерживает автоматическое обновление image через Image Updater

