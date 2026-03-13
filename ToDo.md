# План розробки Grafana Dashboard для моніторингу локальної інфраструктури

Цей документ описує покроковий архітектурний та імплементаційний план для побудови production-ready системи моніторингу на базі Grafana, Prometheus, Loki та Grafana Alloy з використанням Docker.

## 1. Архітектура системи

### Взаємодія компонентів
- **Grafana Alloy:** Єдиний агент (телеметричний колектор), який збирає логи з оброблюваних сервісів та передає їх до Loki. Може також збирати метрики та діяти як Prometheus-агент, але зазвичай Prometheus працює самостійно для server-pull метрик.
- **Prometheus:** База даних часових рядів (TSDB). Виконує періодичний pull (збирання) метрик з експортерів та безпосередньо з FastAPI додатку.
- **Loki:** Система агрегації логів, яка отримує потік даних (push) від Grafana Alloy, індексує метадані (лейбли) та зберігає сирі логи для запитів з Grafana.
- **Grafana:** Візуалізаційний інтерфейс. Виконує ролі клієнта, підключаючись до Prometheus (через PromQL) та Loki (через LogQL) для відображення панелей та налаштування алертів.

### Потік даних
- **Метрики:** Сервіси генерують метрики у форматі Prometheus (через вбудовані бібліотеки або окремі експортери). Prometheus опитує їх через HTTP-маршрути `/metrics`, зберігає локально.
- **Логи:** Сервіси пишуть логи в `stdout/stderr` (обробляються Docker) або у файли. Grafana Alloy читає ці дані, трансформує їх, додає єдині лейбли та відправляє до Loki через HTTP API.
- **Візуалізація:** Grafana робить запити до внутрішніх кінцевих точок `http://prometheus:9090` та `http://loki:3100`.

### Комунікація в Docker Network
Усі сервіси (моніторинг та аплікація) повинні знаходитися в спільній Docker-мережі (наприклад, `monitoring_network`), що дозволяє їм взаємодіяти через імена контейнерів (DNS). Порти назовні прокидаються лише для тих сервісів, які потребують зовнішнього доступу (Grafana, FastAPI, Nginx).

---

## 2. Стратегія збору метрик

### Необхідні метрики за компонентами
- **FastAPI:** Кількість HTTP запитів, тривалість запитів (latency), кількість помилок, статус-коди (4xx, 5xx), кількість активних з'єднань.
  - *Інтеграція:* Бібліотека `prometheus-client` або middleware (наприклад, `prometheus-fastapi-instrumentator`).
- **Nginx:** Вхідні з'єднання, кількість оброблених запитів, час відповіді (upstream response time), статус-коди.
  - *Експортер:* `nginx-prometheus-exporter` (потребує увімкнення `stub_status` в Nginx) або `grafana-alloy` з модулем обробки Nginx.
- **Postfix:** Розмір черги (active, deferred, hold), кількість відправлених/відхилених листів, помилки SMTP.
  - *Експортер:* `postfix_exporter`.
- **Dovecot:** Кількість активних IMAP/POP3 сесій, успішні/неуспішні авторизації, помилки доступу.
  - *Експортер:* `dovecot_exporter`.
- **Host/Container Resources:** Використання CPU, пам'яті (RAM), дискового простору, мережевого трафіку.
  - *Експортер:* `node_exporter` (для хоста), `cAdvisor` (для контейнерів).

---

## 3. Архітектура логування

### Роль Grafana Alloy
Grafana Alloy буде збирати логи через читання локальних файлів (якщо логи пишуться на диск через volumes) або через збір логів безпосередньо від Docker daemon.

### Джерела логів
- **FastAPI:** Application logs (формат JSON) - події бізнес-логіки.
- **Nginx:** Access logs та Error logs.
- **Postfix/Dovecot:** Логи поштових транзакцій (`/var/log/mail.log` або `stdout`).

### Структурування та лейблювання
LogQL покладається на правильне лейблювання. Grafana Alloy повинен додавати наступні лейбли:
- `job`: ім'я сервісу (наприклад, `fastapi`, `nginx`).
- `container_name`: ім'я Docker-контейнера.
- `level`: рівень логу (info, error, warn).

Приклад Alloy конфігурації для локальних Docker логів:
```alloy
// Extract logs from local Docker engine using docker.logs component
loki.source.docker "local_docker" {
  host = "unix:///var/run/docker.sock"
  targets = [
    {__address__ = "localhost", container_name = "fastapi-app", job = "fastapi"},
    {__address__ = "localhost", container_name = "nginx-proxy", job = "nginx"}
  ]
  forward_to = [loki.write.local_loki.receiver]
}

loki.write "local_loki" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

---

## 4. Конфігурація Prometheus

Прописується класичний `prometheus.yml`. Для локального Docker середовища можна використовувати `static_configs` з іменами контейнерів.

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['fastapi-app:8000']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'postfix'
    static_configs:
      - targets: ['postfix-exporter:9154']

  - job_name: 'dovecot'
    static_configs:
      - targets: ['dovecot-exporter:9166']

  - job_name: 'cadvisor' # Container metrics
    static_configs:
      - targets: ['cadvisor:8080']
```

---

## 5. Графана Data Sources

Для автоматизації деплойменту Data Sources налаштовуються через директорію `provisioning/datasources/`.

```yaml
# provisioning/datasources/datasources.yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
```

---

## 6. Дизайн дашборду

Дашборд структурується через "Rows" (рядки), що групують тематичні панелі.

1. **System Health & Resources:** Глобальний погляд (CPU, RAM, Disk, Uptime) для всіх контейнерів.
2. **API Performance (FastAPI):** Latency (p95, p99), RPM (Requests Per Minute), Error Rate (HTTP 5xx).
3. **Mail Activity (Postfix & Dovecot):** Розмір черги листів, вхідні/вихідні листи, активні IMAP з'єднання, помилки авторизації.
4. **Proxy Traffic (Nginx):** Розподіл HTTP-статусів, час відповіді upstream.
5. **Errors & Logs:** Агрегована таблиця помилок з Loki.

---

## 7. Панелі та візуалізації (з прикладами запитів)

### System Health
- **Візуалізація:** Time series / Stat
- **PromQL (Memory usage by container):** 
  ```promql
  sum by (container_label_com_docker_compose_service) (container_memory_usage_bytes{container_label_com_docker_compose_service!=""})
  ```

### API Performance
- **Візуалізація:** Time series / Gauge
- **PromQL (p95 API Latency):**
  ```promql
  histogram_quantile(0.95, sum(rate(fastapi_requests_duration_seconds_bucket[5m])) by (le, endpoint))
  ```

### Nginx Traffic
- **Візуалізація:** Bar gauge / Pie chart (HTTP Status codes)
- **PromQL (Error Rate):**
  ```promql
  sum(rate(nginx_http_requests_total{status=~"5.."}[5m])) / sum(rate(nginx_http_requests_total[5m]))
  ```

### Mail Activity (Postfix)
- **Візуалізація:** Stat
- **PromQL (Queue Size):**
  ```promql
  postfix_queue_length{queue="deferred"}
  ```

### Logs View
- **Візуалізація:** Logs
- **LogQL (FastAPI Errors):**
  ```logql
  {job="fastapi"} |= "ERROR" | json
  ```

---

## 8. Стратегія алертингу

Алерти налаштовуються через Prometheus (на рівні `alert.rules.yml`) або в системі Grafana Alerting. 
Основні критерії:
1. **High API Latency:** Якщо p95 latency > 500ms протягом 5 хвилин.
2. **High Error Rate:** Якщо відсоток HTTP 5xx > 5% протягом 5 хвилин.
3. **High SMTP Queue:** Якщо `postfix_queue_length{queue="deferred"}` > 100 листів.
4. **Authentication Failures:** Зростання невдалих спроб входу в Dovecot (захист від brute-force).
5. **Resource Exhaustion:** Використання контейнером >90% виділеної оперативної пам'яті.

---

## 9. Best Practices

1. **Labeling Strategy:** Зберігайте мінімальний, але стандартизований набір лейблів (напр., `env`, `service`, `instance`). Уникайте лейблів з високою кардинальністю (high cardinality), таких як User-ID або URL зі змінними параметрами.
2. **Maintainability:** Усі конфігурації дашбордів (у форматі JSON) та datasources повинні знаходитися у системі контролю версій та підтягуватися через механізм Grafana Provisioning (Configuration as Code).
3. **Scaling:** У разі розширення системи та переходу від Docker Compose до Kubernetes:
   - Grafana Alloy можна запустити як DaemonSet.
   - Замість `static_configs` використовувати `kubernetes_sd_configs` в Prometheus.
   - Розподілити Loki на компоненти (read/write path) для високої доступності.

---

## 10. Покроковий план імплементації

Даний план розроблений для системного впровадження моніторингу з дотриманням принципів стабільності та масштабованості.

### Фаза 1: Підготовка інфраструктури та базового стеку
1. **Створення Docker-мережі:** Переконатися у наявності `monitoring_network` для ізольованого обміну даними між компонентами.
2. **Розширення `docker-compose.yml`:**
   - Додати сервіс **Loki** для агрегації логів з відповідними volumes для збереження даних.
   - Додати сервіс **Grafana Alloy** з доступом до `/var/run/docker.sock` для збору телеметрії.
   - Сконфігурувати залежності (`depends_on`) для коректного порядку запуску.

### Фаза 2: Інструментація та збір метрик
3. **FastAPI (Application level):**
   - Додати `prometheus-fastapi-instrumentator` у `requirements.txt`.
   - Інтегрувати middleware у файл `app/main.py` та налаштувати експозицію маршруту `/metrics`.
4. **Інфраструктурні експортери:**
   - Додати `node_exporter` (моніторинг ресурсів хоста) та `cAdvisor` (метрики контейнерів) у `docker-compose.yml`.
   - В налаштуваннях Nginx активувати модуль `stub_status` та додати `nginx-prometheus-exporter`.
   - Розгорнути `postfix_exporter` та `dovecot_exporter` для моніторингу поштової підсистеми.
5. **Оновлення конфігурації Prometheus:** Додати всі нові таргети у `monitoring/prometheus/prometheus.yml`.

### Фаза 3: Побудова системи логування
6. **Налаштування Grafana Alloy:**
   - Створити файл конфігурації `config.alloy` на основі наданого шаблону.
   - Визначити правила лейблювання для розділення логів за сервісами (`job`, `container_name`).
7. **Верифікація пайплайну:** Перевірити надходження логів у Loki через "Explore" інтерфейс Grafana.

### Фаза 4: Візуалізація та Configuration as Code
8. **Provisioning Data Sources:** Створити `monitoring/grafana/provisioning/datasources/datasources.yaml` для автоматичного підключення Prometheus та Loki.
9. **Розробка Дашборду:**
   - Створити панелі згідно з дизайном (Rows: System, API, Mail, Proxy, Logs).
   - Використати заздалегідь підготовлені PromQL та LogQL запити.
   - Експортувати дашборд у JSON та налаштувати його автоматичне завантаження через `provisioning/dashboards/`.

### Фаза 5: Алертинг та фіналізація
10. **Налаштування правил сповіщень:**
    - Створити файл `alert.rules.yml` для Prometheus з описаними критеріями (Latency, Error Rate, Queue Size).
    - Налаштувати контактні точки (Contact Points) у Grafana для оперативного інформування.
11. **Тестування та валідація:** Симулювати навантаження та помилки для перевірки відображення на дашборді та спрацювання алертингу.

### Фаза 6: Налаштування Grafana Dashboards (Візуалізація)
12. **Вхід у Grafana:**
    - Перейти за адресою `http://localhost:3000` (через SSH тунель) або `http://<server-ip>:3000`.
    - Логін: `admin`, Пароль: `admin`.

13. **Імпорт базових дашбордів (за ID):**
    - В меню вибрати **Dashboards** -> **New** -> **Import**.
    - **Сервер (Node Exporter):** Введіть ID `1860`. Це "Node Exporter Full" — найкращий дашборд для моніторингу CPU, RAM, Disk та мережі хоста.
    - **Nginx:** Введіть ID `11199`. Спеціалізований дашборд для `nginx-prometheus-exporter`. Показує кількість запитів, активні з'єднання та помилки.
    - **Docker (cAdvisor):** Введіть ID `14282`. Показує використання ресурсів кожним окремим контейнером.
    - **FastAPI:** Введіть ID `16110`. Дашборд, оптимізований під `prometheus-fastapi-instrumentator`. Відображає Latency (p95/p99), Request Rate та Status Codes.

14. **Створення дашборду для Пошти (Postfix & Dovecot):**
    - Оскільки універсальні ID для пошти часто потребують складної адаптації, рекомендується створити власну панель:
    - **Postfix (Queue):** Створити панель типу "Stat". Запит: `postfix_queue_length`. В легенді вказати `{{queue}}`.
    - **Dovecot (Auth):** Створити панель типу "Time series". Запит: `rate(dovecot_auth_success_total[5m])` для успішних входів та `rate(dovecot_auth_failed_total[5m])` для помилок.

15. **Налаштування логів (Loki):**
    - Використовувати вкладку **Explore** у Grafana.
    - Обрати джерело даних **Loki**.
    - Використати фільтр `{job="docker_logs"}` для перегляду логів всіх контейнерів у реальному часі.
