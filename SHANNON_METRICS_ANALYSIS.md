# Анализ Метрик и Данных Shannon для Дашборда

## 📋 Обзор

Shannon генерирует богатый набор данных, которые можно использовать для создания комплексного дашборда. Все данные структурированы и доступны в JSON и Markdown форматах.

---

## 📁 Структура Выходных Данных

```
audit-logs/{hostname}_{sessionId}/
├── session.json                    # ⭐ ОСНОВНОЙ ФАЙЛ С МЕТРИКАМИ
├── workflow.log                    # Лог выполнения workflow
├── deliverables/                   # Отчеты и результаты
│   ├── comprehensive_security_assessment_report.md
│   ├── pre_recon_deliverable.md
│   ├── recon_deliverable.md
│   ├── code_analysis_deliverable.md
│   ├── injection_analysis_deliverable.md
│   ├── injection_exploitation_evidence.md
│   ├── xss_analysis_deliverable.md
│   ├── xss_exploitation_evidence.md
│   ├── auth_analysis_deliverable.md
│   ├── auth_exploitation_evidence.md
│   ├── authz_analysis_deliverable.md
│   ├── authz_exploitation_evidence.md
│   ├── ssrf_analysis_deliverable.md
│   ├── ssrf_exploitation_evidence.md
│   ├── injection_exploitation_queue.json
│   ├── xss_exploitation_queue.json
│   ├── auth_exploitation_queue.json
│   ├── authz_exploitation_queue.json
│   └── ssrf_exploitation_queue.json
├── agents/                         # Логи выполнения агентов
│   └── {timestamp}_{agent}_attempt-{n}.log
└── prompts/                        # Промпты использованные в сессии
    └── {agent}.md
```

---

## 🎯 Основной Источник Данных: session.json

### Полная Структура session.json

```typescript
interface SessionData {
  session: {
    id: string;                      // ID сессии (workflow ID)
    webUrl: string;                  // URL тестируемого приложения
    repoPath?: string;               // Путь к репозиторию
    status: 'in-progress' | 'completed' | 'failed';
    createdAt: string;              // ISO timestamp
    completedAt?: string;            // ISO timestamp (если завершено)
  };
  metrics: {
    total_duration_ms: number;       // Общее время выполнения
    total_cost_usd: number;          // Общая стоимость
    phases: Record<string, PhaseMetrics>;
    agents: Record<string, AgentMetrics>;
  };
}

interface PhaseMetrics {
  duration_ms: number;               // Длительность фазы
  duration_percentage: number;       // Процент от общего времени
  cost_usd: number;                  // Стоимость фазы
  agent_count: number;               // Количество агентов в фазе
}

interface AgentMetrics {
  status: 'in-progress' | 'success' | 'failed';
  attempts: AttemptData[];           // Массив попыток (retries)
  final_duration_ms: number;         // Финальная длительность
  total_cost_usd: number;            // Общая стоимость (включая failed attempts)
  model?: string;                    // Модель AI использованная
  checkpoint?: string;                // Git commit hash
}

interface AttemptData {
  attempt_number: number;            // Номер попытки
  duration_ms: number;               // Длительность попытки
  cost_usd: number;                  // Стоимость попытки
  success: boolean;                  // Успешна ли попытка
  timestamp: string;                // ISO timestamp
  model?: string;                    // Модель AI
  error?: string;                    // Ошибка (если failed)
}
```

---

## 📊 Метрики Доступные для Дашборда

### 1. **Метрики Сессии (Session Level)**

#### Основная Информация
- ✅ **Session ID** - уникальный идентификатор
- ✅ **Target URL** - тестируемое приложение
- ✅ **Repository Path** - путь к исходному коду
- ✅ **Status** - статус выполнения (in-progress/completed/failed)
- ✅ **Created At** - время начала
- ✅ **Completed At** - время завершения
- ✅ **Total Duration** - общее время выполнения (мс)
- ✅ **Total Cost** - общая стоимость в USD

#### Вычисляемые Метрики
- ⚡ **Elapsed Time** - прошедшее время (если in-progress)
- ⚡ **Progress Percentage** - процент завершения
- ⚡ **Cost per Hour** - стоимость в час
- ⚡ **Average Cost per Agent** - средняя стоимость агента

---

### 2. **Метрики по Фазам (Phase Level)**

#### Доступные Фазы
1. **pre-recon** - Pre-Reconnaissance
2. **recon** - Reconnaissance
3. **vulnerability-analysis** - Vulnerability Analysis
4. **exploitation** - Exploitation
5. **reporting** - Reporting

#### Метрики для Каждой Фазы
- ✅ **Duration (ms)** - длительность фазы
- ✅ **Duration Percentage** - процент от общего времени
- ✅ **Cost (USD)** - стоимость фазы
- ✅ **Agent Count** - количество агентов в фазе

#### Вычисляемые Метрики
- ⚡ **Average Duration per Agent** - средняя длительность агента
- ⚡ **Average Cost per Agent** - средняя стоимость агента
- ⚡ **Phase Efficiency** - соотношение найденных уязвимостей к стоимости

---

### 3. **Метрики по Агентам (Agent Level)**

#### Доступные Агенты
- `pre-recon` - Pre-Reconnaissance
- `recon` - Reconnaissance
- `injection-vuln` - Injection Vulnerability Analysis
- `xss-vuln` - XSS Vulnerability Analysis
- `auth-vuln` - Authentication Vulnerability Analysis
- `authz-vuln` - Authorization Vulnerability Analysis
- `ssrf-vuln` - SSRF Vulnerability Analysis
- `exploit-injection` - Injection Exploitation
- `exploit-xss` - XSS Exploitation
- `exploit-auth` - Authentication Exploitation
- `exploit-authz` - Authorization Exploitation
- `exploit-ssrf` - SSRF Exploitation

#### Метрики для Каждого Агента
- ✅ **Status** - статус (in-progress/success/failed)
- ✅ **Final Duration** - финальная длительность (мс)
- ✅ **Total Cost** - общая стоимость (USD)
- ✅ **Model** - модель AI использованная
- ✅ **Checkpoint** - Git commit hash
- ✅ **Attempts** - массив попыток с деталями

#### Метрики Попыток (Attempts)
- ✅ **Attempt Number** - номер попытки
- ✅ **Duration** - длительность попытки
- ✅ **Cost** - стоимость попытки
- ✅ **Success** - успешна ли попытка
- ✅ **Timestamp** - время попытки
- ✅ **Model** - модель AI
- ✅ **Error** - ошибка (если failed)

#### Вычисляемые Метрики
- ⚡ **Retry Count** - количество повторных попыток
- ⚡ **Success Rate** - процент успешных попыток
- ⚡ **Average Attempt Duration** - средняя длительность попытки
- ⚡ **Total Failed Cost** - стоимость неудачных попыток

---

### 4. **Метрики Уязвимостей (Vulnerability Level)**

#### Источники Данных
1. **Exploitation Queue JSON** (`*_exploitation_queue.json`)
2. **Exploitation Evidence Markdown** (`*_exploitation_evidence.md`)
3. **Final Report** (`comprehensive_security_assessment_report.md`)

#### Структура Queue JSON
```json
{
  "vulnerabilities": [
    {
      "id": "INJ-VULN-01",
      "title": "SQL Injection Authentication Bypass",
      "severity": "Critical",
      "location": "POST /rest/user/login",
      "status": "exploited"
    }
  ]
}
```

#### Извлекаемые Метрики
- ✅ **Total Vulnerabilities Found** - всего найдено
- ✅ **Vulnerabilities by Type** - по типам (Injection, XSS, Auth, etc.)
- ✅ **Vulnerabilities by Severity** - по критичности (Critical/High/Medium/Low)
- ✅ **Exploited Count** - количество успешно эксплуатированных
- ✅ **Exploitation Rate** - процент успешной эксплуатации
- ✅ **Vulnerability Locations** - места обнаружения (endpoints, files)

#### Детали Уязвимостей (из Markdown)
- ✅ **Vulnerability ID** - уникальный ID
- ✅ **Title** - название
- ✅ **Severity** - критичность
- ✅ **Location** - местонахождение (endpoint, file)
- ✅ **Impact** - описание воздействия
- ✅ **Prerequisites** - требования для эксплуатации
- ✅ **Exploitation Steps** - шаги эксплуатации
- ✅ **Proof of Impact** - доказательство воздействия
- ✅ **Code References** - ссылки на код

---

### 5. **Метрики Производительности (Performance Metrics)**

#### Из session.json
- ✅ **Total Duration** - общее время
- ✅ **Phase Durations** - длительности фаз
- ✅ **Agent Durations** - длительности агентов
- ✅ **Attempt Durations** - длительности попыток

#### Вычисляемые Метрики
- ⚡ **Average Phase Duration** - средняя длительность фазы
- ⚡ **Longest Phase** - самая долгая фаза
- ⚡ **Shortest Phase** - самая короткая фаза
- ⚡ **Phase Distribution** - распределение времени по фазам
- ⚡ **Agent Efficiency** - эффективность агентов (уязвимости/время)

---

### 6. **Метрики Стоимости (Cost Metrics)**

#### Из session.json
- ✅ **Total Cost** - общая стоимость
- ✅ **Phase Costs** - стоимость фаз
- ✅ **Agent Costs** - стоимость агентов
- ✅ **Attempt Costs** - стоимость попыток
- ✅ **Failed Attempt Costs** - стоимость неудачных попыток

#### Вычисляемые Метрики
- ⚡ **Cost per Vulnerability** - стоимость на уязвимость
- ⚡ **Cost per Critical Vulnerability** - стоимость на критическую уязвимость
- ⚡ **Cost per Hour** - стоимость в час
- ⚡ **Average Cost per Agent** - средняя стоимость агента
- ⚡ **Cost Efficiency** - эффективность затрат
- ⚡ **ROI Metrics** - метрики возврата инвестиций

---

### 7. **Метрики Моделей AI (AI Model Metrics)**

#### Из session.json
- ✅ **Models Used** - список использованных моделей
- ✅ **Model per Agent** - модель для каждого агента
- ✅ **Model per Attempt** - модель для каждой попытки

#### Вычисляемые Метрики
- ⚡ **Model Distribution** - распределение по моделям
- ⚡ **Model Performance** - производительность моделей
- ⚡ **Model Cost Comparison** - сравнение стоимости моделей
- ⚡ **Model Success Rate** - процент успеха по моделям

---

### 8. **Метрики Качества (Quality Metrics)**

#### Из Deliverables
- ✅ **Deliverables Created** - созданные deliverables
- ✅ **Report Completeness** - полнота отчетов
- ✅ **Evidence Quality** - качество доказательств

#### Вычисляемые Метрики
- ⚡ **False Positive Rate** - процент ложных срабатываний (если есть данные)
- ⚡ **Exploitation Success Rate** - процент успешной эксплуатации
- ⚡ **Coverage Metrics** - метрики покрытия тестирования

---

### 9. **Метрики Времени (Timeline Metrics)**

#### Из session.json и логов
- ✅ **Start Time** - время начала
- ✅ **End Time** - время завершения
- ✅ **Phase Start Times** - время начала фаз
- ✅ **Agent Start Times** - время начала агентов
- ✅ **Attempt Timestamps** - временные метки попыток

#### Вычисляемые Метрики
- ⚡ **Timeline Visualization** - визуализация временной линии
- ⚡ **Phase Transitions** - переходы между фазами
- ⚡ **Bottlenecks** - узкие места по времени
- ⚡ **Parallel Execution** - параллельное выполнение агентов

---

### 10. **Метрики Ошибок (Error Metrics)**

#### Из session.json и логов
- ✅ **Failed Agents** - список неудачных агентов
- ✅ **Error Messages** - сообщения об ошибках
- ✅ **Retry Counts** - количество повторных попыток
- ✅ **Error Types** - типы ошибок

#### Вычисляемые Метрики
- ⚡ **Error Rate** - процент ошибок
- ⚡ **Error Distribution** - распределение ошибок
- ⚡ **Recovery Rate** - процент восстановления после ошибок
- ⚡ **Most Common Errors** - наиболее частые ошибки

---

## 📈 Рекомендуемые Виджеты для Дашборда

### 1. **Обзорная Панель (Overview Dashboard)**

#### Виджеты
- 📊 **KPI Cards:**
  - Total Sessions
  - Active Sessions
  - Total Vulnerabilities Found
  - Total Cost
  - Average Duration
  - Success Rate

- 📈 **Charts:**
  - Sessions Over Time (line chart)
  - Vulnerabilities by Type (pie chart)
  - Cost Trend (area chart)
  - Success Rate Trend (line chart)

---

### 2. **Детальная Панель Сессии (Session Detail)**

#### Виджеты
- 📋 **Session Info:**
  - Session ID, Target URL, Status
  - Start/End Time, Duration
  - Total Cost

- 📊 **Phase Breakdown:**
  - Phase Duration Chart (bar chart)
  - Phase Cost Chart (bar chart)
  - Phase Progress (progress bars)

- 📈 **Agent Metrics:**
  - Agent Status Grid
  - Agent Duration Comparison
  - Agent Cost Comparison
  - Agent Success Rate

- 🔄 **Timeline:**
  - Gantt Chart фаз и агентов
  - Timeline с событиями

---

### 3. **Панель Уязвимостей (Vulnerabilities Dashboard)**

#### Виджеты
- 📊 **Vulnerability Overview:**
  - Total by Type (bar chart)
  - Total by Severity (pie chart)
  - Exploitation Rate (gauge)
  - Vulnerabilities Over Time (line chart)

- 📋 **Vulnerability List:**
  - Таблица всех уязвимостей
  - Фильтры: Type, Severity, Status
  - Сортировка: Severity, Date, Type

- 🔍 **Vulnerability Detail:**
  - Детальная информация об уязвимости
  - Exploitation Steps
  - Proof of Impact
  - Code References

---

### 4. **Панель Производительности (Performance Dashboard)**

#### Виджеты
- ⏱️ **Duration Metrics:**
  - Average Duration by Phase
  - Duration Distribution
  - Longest/Shortest Sessions
  - Duration Trend

- 💰 **Cost Metrics:**
  - Cost by Phase
  - Cost per Vulnerability
  - Cost Trend
  - Cost Efficiency

- 🎯 **Efficiency Metrics:**
  - Vulnerabilities per Hour
  - Cost per Critical Vulnerability
  - Agent Efficiency Comparison

---

### 5. **Панель Аналитики (Analytics Dashboard)**

#### Виджеты
- 📊 **Trends:**
  - Sessions Over Time
  - Vulnerabilities Over Time
  - Cost Over Time
  - Success Rate Over Time

- 🔍 **Comparisons:**
  - Phase Comparison
  - Agent Comparison
  - Model Comparison
  - Target Comparison

- 📈 **Predictions:**
  - Estimated Completion Time
  - Estimated Cost
  - Risk Assessment

---

## 🔧 API Endpoints для Бекенда

### Рекомендуемая Структура API

```typescript
// Sessions
GET    /api/sessions                    // Список всех сессий
GET    /api/sessions/:id                // Детали сессии
GET    /api/sessions/:id/metrics        // Метрики сессии
GET    /api/sessions/:id/phases         // Метрики по фазам
GET    /api/sessions/:id/agents         // Метрики по агентам
GET    /api/sessions/:id/vulnerabilities // Уязвимости сессии
GET    /api/sessions/:id/timeline       // Временная линия

// Vulnerabilities
GET    /api/vulnerabilities              // Все уязвимости
GET    /api/vulnerabilities/:id          // Детали уязвимости
GET    /api/vulnerabilities/stats        // Статистика уязвимостей
GET    /api/vulnerabilities/by-type      // По типам
GET    /api/vulnerabilities/by-severity  // По критичности

// Analytics
GET    /api/analytics/overview           // Общая статистика
GET    /api/analytics/trends             // Тренды
GET    /api/analytics/comparisons        // Сравнения
GET    /api/analytics/efficiency         // Эффективность

// Real-time
WS     /ws/sessions/:id                  // WebSocket для real-time обновлений
```

---

## 📊 Примеры Данных для Виджетов

### 1. KPI Cards Data

```json
{
  "totalSessions": 150,
  "activeSessions": 3,
  "totalVulnerabilities": 1250,
  "totalCost": 7500.50,
  "averageDuration": 5400000,
  "successRate": 0.95
}
```

### 2. Vulnerabilities by Type

```json
{
  "injection": 450,
  "xss": 320,
  "auth": 280,
  "authz": 150,
  "ssrf": 50
}
```

### 3. Phase Metrics

```json
{
  "phases": [
    {
      "name": "pre-recon",
      "duration": 300000,
      "cost": 2.50,
      "agentCount": 1,
      "percentage": 5.5
    },
    {
      "name": "recon",
      "duration": 600000,
      "cost": 5.00,
      "agentCount": 1,
      "percentage": 11.1
    }
  ]
}
```

### 4. Timeline Data

```json
{
  "events": [
    {
      "timestamp": "2026-02-04T18:21:34Z",
      "type": "phase_start",
      "phase": "pre-recon",
      "agent": "pre-recon"
    },
    {
      "timestamp": "2026-02-04T18:26:34Z",
      "type": "phase_complete",
      "phase": "pre-recon",
      "agent": "pre-recon"
    }
  ]
}
```

---

## 🎨 Рекомендации по Визуализации

### Цветовая Схема
- 🟢 **Success** - зеленый
- 🔴 **Failed** - красный
- 🟡 **In Progress** - желтый
- 🔵 **Info** - синий
- 🟣 **Warning** - фиолетовый

### Графики
- **Line Charts** - для трендов во времени
- **Bar Charts** - для сравнений
- **Pie Charts** - для распределений
- **Gauge Charts** - для процентов и rates
- **Gantt Charts** - для временных линий
- **Heatmaps** - для матриц данных
- **Tree Maps** - для иерархических данных

---

## 🔄 Real-time Обновления

### WebSocket Events

```typescript
// Session Updates
{
  "type": "session_update",
  "data": {
    "sessionId": "...",
    "status": "in-progress",
    "currentPhase": "recon",
    "currentAgent": "recon",
    "progress": 0.35
  }
}

// Agent Updates
{
  "type": "agent_update",
  "data": {
    "sessionId": "...",
    "agent": "recon",
    "status": "success",
    "duration": 600000,
    "cost": 5.00
  }
}

// Vulnerability Found
{
  "type": "vulnerability_found",
  "data": {
    "sessionId": "...",
    "vulnerability": {
      "id": "INJ-VULN-01",
      "type": "injection",
      "severity": "critical"
    }
  }
}
```

---

## 📝 Итоговый Список Метрик

### Доступные Метрики (100+)

#### Session Level (10+ метрик)
- ID, URL, Status, Duration, Cost, Start/End Time, Progress

#### Phase Level (20+ метрик)
- 5 фаз × (Duration, Cost, Agent Count, Percentage, Efficiency)

#### Agent Level (60+ метрик)
- 12 агентов × (Status, Duration, Cost, Attempts, Model, Success Rate)

#### Vulnerability Level (30+ метрик)
- Count, Type Distribution, Severity Distribution, Exploitation Rate, Locations

#### Performance Level (15+ метрик)
- Duration Metrics, Cost Metrics, Efficiency Metrics

#### Quality Level (10+ метрик)
- Success Rate, Error Rate, Coverage Metrics

---

## 🚀 Следующие Шаги

1. ✅ **Создать парсеры** для session.json и deliverables
2. ✅ **Создать API** для доступа к данным
3. ✅ **Создать дашборд** с виджетами
4. ✅ **Добавить real-time** обновления через WebSocket
5. ✅ **Добавить аналитику** и сравнения

---

## 📚 Дополнительные Источники Данных

### Workflow Log
- Детальные логи выполнения
- События workflow
- Ошибки и предупреждения

### Agent Logs
- Детальные логи агентов
- LLM responses
- Tool calls
- Screenshots (если есть)

### Prompts
- Использованные промпты
- Конфигурация агентов
- Переменные окружения

---

**Все данные структурированы и готовы для использования в дашборде!** 🎉

