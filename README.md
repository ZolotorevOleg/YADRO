# currency_service

HTTP-сервис для получения курсов валют через API ЦБ РФ.

## Функциональность

- `GET /info`
- `GET /info/currency?date=YYYY-MM-DD`
- `GET /info/currency?currency=USD`
- `GET /info/currency?date=YYYY-MM-DD&currency=USD`

## Переменные окружения

- `VERSION` — версия приложения, по умолчанию `1.0.0`
- `AUTHOR` — автор приложения, по умолчанию `o.zolotorev1`
- `PORT` — порт запуска приложения, по умолчанию `8000`


## Docker Hub

Образ:

`z0leg/currency-service`

## Безопасность
- запуск от non-root пользователя
- read-only файловая система (hardened)
- cap_drop: ALL
- no-new-privileges
- tmpfs для /tmp
- лимиты ресурсов
- healthcheck

## Сканирование
- Trivy → trivy-report.json
- SBOM  → sbom.json

# CI/CD

### В проекте реализован CI/CD pipeline на базе Jenkins Multibranch Pipeline

# Pipeline стадии
- # Setup Python
    - установка библиотек
    - настройка окружения
- # Quality
    - # Lint
        - проверка кода через flake8 `(отчет сохраняется артефактом)`
        - проверка Dockerfile через hadolint `(отчет сохраняется артефактом)`
    - # SAST (Bandit)
        - проверка кода приложения
        - `(отчет сохраняется артефактом)`
- # Test
    - запуск unit-тестов `(отчет сохраняется артефактом)`
- # Build
    - сборка Docker-образа
- # Publish to DockerHub
    - [z0leg/currency-service](https://hub.docker.com/r/z0leg/currency-service)
- # Deploy (deploy-job)
    - в staging при commit в main ветку
    - в production при добавлении тега на commit
    - вызывает deploy-job с параметрами тега и окружения
- # Smoke Test (curl)
    - в том окружении, где осуществился деплой контейнера
    - проверка доступности приложения по адресу http://localhost:8000/info
- # Security
    - ## Pre-commit
        - проверка на EOF, trailing-whitespace, проверка yaml файлов
        - detect-secrets
        -  `отчет сохраняется артефактом`
    - ## SCA (Trivy)
        - анализ уязвимостей запушенного Docker-образа
        - запускается через Docker-контейнер
        -  `отчет сохраняется артефактом`
    - ## K6
        - нагрузочный тест с 10 виртуальными пользователями в течении 30 секунд
        - условия успешности теста: ошибок < 50%, 95% запросов быстрее 500ms
        - запросы на `/info` `/info/currency`
        -  `отчет сохраняется артефактом`
    - ## DAST ZAP
        - поиск уязвимостей в работающем веб приложении
        - запускается через Docker-контейнер
        - `отчет сохраняется артефактом`
- # Generate changelog
    - только после деплоя в production
    - собираются последние 20 строчек из логов в файл и сохраняются артефактом

# Триггеры pipeline
- ## feature-ветка
    - запуск проверок `(lint, SAST, test)`
- ## Merge Request
    - запуск проверок `(lint, SAST, test)`
    - сборка образа `(build)`
- ## Push в master
    - полный pipeline с деплоем в staging и запуск `secure-tests`
- ## Git tag (v*)
    - полный pipeline с деплоем в production и сохранением `changelog`

# Отчёты

## Отчёты сохраняются в Jenkins (archiveArtifacts):

- `reports/bandit.json` — SAST
- `reports/bandit.txt` — SAST
- `reports/flake8.txt` — flake8
- `reports/hadoolint.txt` — hadoolint
- `reports/k6.txt` — нагрузочное тестирование
- `reports/k6-script.js` — скрипт запуска нагрузочного тестирования
- `reports/precommit.txt` — secrets scan
- `reports/tests.xml` — pytest
- `reports/trivy-image.json` — SCA
- `reports/zap-report.html` — DAST
- `reports/zap-report.json` — DAST
- `reports/changelog.md` — релиз

# Тестирование поведения pipeline
Тестирование было проведено на новой ветке master, которая имитировала поведение main ветки. Pipeline отработал корректно по всем триггерам


# Ansible

В проекте реализована автоматизация развертывания Kubernetes-кластера с помощью Ansible.

## Роли

Используются следующие роли:

- **crio**
  - установка и настройка CRI-O
  - поддержка proxy (через Ansible Vault)
- **kubelet**
  - установка kubelet
  - настройка и включение сервиса
- **kubeadm**
  - инициализация control plane
  - автоматическое подключение worker-нод
  - установка CNI (Calico)

## Структура

```
ansible/
├── inventory/
│   ├── hosts.ini
│   └── group_vars/
├── playbooks/
│   └── site.yml
└── roles/
    ├── crio/
    ├── kubelet/
    └── kubeadm/
```
## Inventory

Кластер состоит из:

- 1 `control-plane` нода
- 2 `worker` нод

## Запуск
```bash
ansible-playbook playbooks/site.yml --ask-vault-pass
```
## Vault

Чувствительные данные (proxy логин/пароль) хранятся в зашифрованном виде с помощью `Ansible Vault`.

- переменные вынесены в `group_vars`
- роли имеют безопасные значения по умолчанию
- запуск возможен без передачи дополнительных параметров

## Особенности
- полностью автоматизированный деплой Kubernetes-кластера
- поддержка proxy для установки пакетов
- идемпотентность ролей
- автоматическое подключение worker-нод
- проверка состояния через Molecule

## Тестирование (Molecule)

Для каждой роли реализованы тесты:

- `converge` — применение роли
- `idempotence` — проверка повторного запуска
- `verify` — проверка состояния (сервисы, бинарники)

## Результат

После выполнения:

- все ноды находятся в состоянии `Ready`
- системные pod’ы работают
- сеть (Calico) настроена


## Развёртывание приложения в Kubernetes

Приложение currency-service развернуто в Kubernetes-кластере, состоящем из одной control-plane ноды и двух worker нод.

### Архитектура
```
Интернет
→ Tailscale Funnel (HTTPS)
→ master (Ingress)
→ Service
→ Pods (worker1, worker2)
```
### Используемые ресурсы Kubernetes
- Deployment
- запуск приложения в `2` репликах
- контейнер: [z0leg/currency-service:v1](https://hub.docker.com/r/z0leg/currency-service)
- порт: `8000`

### Дополнительно:

- `readinessProbe` — проверка готовности
- `livenessProbe` — перезапуск при зависании
- `resources` — ограничения CPU и памяти
- `topologySpreadConstraints` — распределение pod’ов по нодам

### Service
- порт: 80 → 8000
- балансировка между pod’ами

### Ingress
- ingressClass: nginx
- маршрут: /info
- host: [currency-service.tailaaac65.ts.net](https://currency-service.tailaaac65.ts.net/info)
- Ingress Controller

Используется NGINX Ingress Controller, развернутый как DaemonSet

### Особенности:

- работает на всех нодах
- используется hostNetwork
- принимает трафик на порту 80
- внешний доступ
- для публикации сервиса используется Tailscale Funnel.

### Причины выбора:

- не требуется белый IP
- автоматически настраивается HTTPS
- не требуется cert-manager
- простая настройка

### Доступ:

https://currency-service.tailaaac65.ts.net/info

### Отказоустойчивость

Обеспечена за счёт:

- 2 реплик приложения
- размещения pod’ов на разных нодах
- автоматического перезапуска pod’ов Kubernetes
- балансировки через Service
- Балансировка нагрузки




# CI/CD и GitOps

Для автоматизации сборки и доставки приложения был настроен CI/CD с использованием ArgoCD и ArgoCD Image Updater.

## Архитектура CI/CD

Git push → Jenkins → Docker build → DockerHub → Secure Tests → ArgoCD Image Updater → ArgoCD → Kubernetes

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

