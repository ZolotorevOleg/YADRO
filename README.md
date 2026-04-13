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
  - установка CNI (Flannel)

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
- сеть (Flannel) настроена
