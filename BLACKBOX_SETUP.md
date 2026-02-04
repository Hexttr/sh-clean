# Black Box Тестирование в Shannon - Настройка и Запуск

## 📋 Краткое Резюме

Black box тестирование в Shannon начинается автоматически после завершения **фазы Pre-Reconnaissance** и использует браузерную автоматизацию через Playwright для динамического тестирования приложения.

---

## ✅ Что Уже Работает

### 1. **Chromium Установлен**
- ✅ Версия: Chromium 143.0.7499.169
- ✅ Путь: `/usr/bin/chromium-browser`
- ✅ Установлен в Docker контейнере

### 2. **Playwright MCP Доступен**
- ✅ Устанавливается через `npx @playwright/mcp@latest`
- ✅ Доступен в контейнере worker

### 3. **Переменные Окружения Настроены**
```bash
SHANNON_DOCKER=true
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser
```

### 4. **MCP Серверы Настраиваются Автоматически**
- ✅ `buildMcpServers()` в `claude-executor.ts` настраивает Playwright MCP
- ✅ Каждому агенту назначается свой Playwright instance

---

## 🎯 Что Нужно Для Black Box Тестирования

### 1. **Завершение Pre-Reconnaissance Фазы**

Black box тестирование начинается **автоматически** после успешного завершения Pre-Reconnaissance.

**Требования:**
- ✅ Pre-recon должен успешно создать `code_analysis_deliverable.md`
- ✅ Workflow должен перейти к фазе Reconnaissance

**Проверка:**
```bash
cd /root/shannon
./shannon query ID=<workflow-id>
```

### 2. **Доступность Целевого Приложения**

Приложение должно быть доступно по указанному URL.

**Для тестирования:**
- Juice Shop уже запущен на `http://localhost:3001`
- Для внешних приложений: убедитесь, что URL доступен из контейнера

**Проверка доступности:**
```bash
docker exec shannon_worker_1 curl -I http://localhost:3001
```

### 3. **Работающие MCP Серверы**

MCP серверы настраиваются автоматически при запуске агента.

**Что происходит:**
1. `buildMcpServers()` создает Playwright MCP сервер
2. Сервер запускается через `npx @playwright/mcp@latest`
3. Используется системный Chromium из контейнера

**Проверка в логах:**
```bash
docker-compose logs worker | grep "MCP:"
# Должно показать: MCP: playwright-agentX(connected), shannon-helper(connected)
```

---

## 🔄 Поток Black Box Тестирования

### Фаза 2: Reconnaissance (Black Box начало)

```
workflows.ts → runReconAgent()
    │
activities.ts → runAgentActivity('recon', ...)
    │
claude-executor.ts → runClaudePrompt()
    │
buildMcpServers() → создает Playwright MCP сервер
    │
Claude AI Agent → использует Playwright инструменты
    │
Браузерная автоматизация:
- navigate() - переход по URL
- click() - клики по элементам
- type() - ввод текста
- screenshot() - скриншоты
- и т.д.
```

### Фазы 3-4: Vulnerability Analysis + Exploitation

Все агенты используют браузерную автоматизацию:
- `vuln-injection` → `exploit-injection`
- `vuln-xss` → `exploit-xss`
- `vuln-auth` → `exploit-auth`
- `vuln-ssrf` → `exploit-ssrf`
- `vuln-authz` → `exploit-authz`

---

## 🛠️ Инструменты Playwright Доступные AI Агенту

### Навигация
- `mcp__playwright__browser_navigate` - переход по URL
- `mcp__playwright__browser_navigate_back` - назад

### Взаимодействие
- `mcp__playwright__browser_click` - клик по элементу
- `mcp__playwright__browser_hover` - наведение
- `mcp__playwright__browser_type` - ввод текста
- `mcp__playwright__browser_press_key` - нажатие клавиш
- `mcp__playwright__browser_fill_form` - заполнение формы
- `mcp__playwright__browser_select_option` - выбор опции
- `mcp__playwright__browser_file_upload` - загрузка файла

### Информация
- `mcp__playwright__browser_snapshot` - снимок страницы
- `mcp__playwright__browser_take_screenshot` - скриншот
- `mcp__playwright__browser_evaluate` - выполнение JS
- `mcp__playwright__browser_console_messages` - сообщения консоли
- `mcp__playwright__browser_network_requests` - сетевые запросы
- `mcp__playwright__browser_tabs` - управление вкладками
- `mcp__playwright__browser_wait_for` - ожидание элементов
- `mcp__playwright__browser_handle_dialog` - обработка диалогов

---

## 📁 Ключевые Файлы для Black Box

### 1. **`src/temporal/workflows.ts`**
**Фаза 2: Reconnaissance**
```typescript
// === Phase 2: Reconnaissance ===
state.currentPhase = 'recon';
state.currentAgent = 'recon';
await a.logPhaseTransition(activityInput, 'recon', 'start');
state.agentMetrics['recon'] = await a.runReconAgent(activityInput);
```

### 2. **`src/temporal/activities.ts`**
**Функция:** `runReconAgent()`
```typescript
export async function runReconAgent(input: ActivityInput): Promise<AgentMetrics> {
  return runAgentActivity('recon', input);
}
```

### 3. **`src/ai/claude-executor.ts`**
**Функция:** `buildMcpServers()`
- Настраивает Playwright MCP сервер
- Указывает путь к Chromium
- Настраивает переменные окружения

### 4. **`prompts/recon.txt`**
- Промпт для Reconnaissance агента
- Инструкции по использованию браузера
- Использует `{{MCP_SERVER}}` для указания Playwright instance

### 5. **`src/constants.ts`**
**MCP_AGENT_MAPPING:**
```typescript
recon: 'playwright-agent2',
'vuln-injection': 'playwright-agent1',
'exploit-injection': 'playwright-agent1',
// и т.д.
```

---

## ⚙️ Настройка Playwright MCP

### Автоматическая Настройка

Playwright MCP настраивается автоматически в `buildMcpServers()`:

```typescript
const mcpArgs: string[] = [
  '@playwright/mcp@latest',
  '--isolated',
  '--user-data-dir', `/tmp/${playwrightMcpName}`,
];

if (isDocker) {
  mcpArgs.push('--executable-path', '/usr/bin/chromium-browser');
  mcpArgs.push('--browser', 'chromium');
}
```

### Переменные Окружения

```typescript
const envVars: Record<string, string> = {
  PLAYWRIGHT_HEADLESS: 'true',
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD: '1', // для Docker
};
```

---

## 🔍 Проверка Работы Black Box

### 1. Проверка Логов

```bash
cd /root/shannon
docker-compose logs worker | grep -E "recon|playwright|browser"
```

**Ожидаемый вывод:**
- `Assigned recon -> playwright-agent2`
- `MCP: playwright-agent2(connected), shannon-helper(connected)`
- Использование инструментов `mcp__playwright__browser_*`

### 2. Проверка Deliverables

После завершения Reconnaissance должен быть создан:
```
audit-logs/<session-id>/deliverables/recon_deliverable.md
```

### 3. Проверка Скриншотов

AI агент может создавать скриншоты:
```
audit-logs/<session-id>/agents/recon/screenshots/
```

### 4. Проверка Workflow

```bash
./shannon query ID=<workflow-id>
```

Должно показать:
- `currentPhase: 'recon'` или `'vulnerability-exploitation'`
- `completedAgents` должен включать `'recon'`

---

## 🚨 Возможные Проблемы и Решения

### Проблема 1: Playwright MCP не запускается

**Симптомы:**
- Ошибки в логах: `Failed to start Playwright MCP`
- `MCP: playwright-agentX(disconnected)`

**Решение:**
1. Проверить доступность `npx`:
   ```bash
   docker exec shannon_worker_1 npx --version
   ```

2. Проверить доступность Playwright MCP:
   ```bash
   docker exec shannon_worker_1 npx @playwright/mcp@latest --help
   ```

3. Пересобрать контейнер:
   ```bash
   cd /root/shannon
   docker-compose build --no-cache worker
   docker-compose up -d worker
   ```

### Проблема 2: Chromium не запускается

**Симптомы:**
- Ошибки: `Failed to launch browser`
- `Chromium executable not found`

**Решение:**
1. Проверить наличие Chromium:
   ```bash
   docker exec shannon_worker_1 which chromium-browser
   ```

2. Проверить переменные окружения:
   ```bash
   docker exec shannon_worker_1 env | grep PLAYWRIGHT
   ```

3. Убедиться, что `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium-browser`

### Проблема 3: Приложение недоступно

**Симптомы:**
- Ошибки навигации: `Navigation timeout`
- `Failed to navigate to URL`

**Решение:**
1. Проверить доступность из контейнера:
   ```bash
   docker exec shannon_worker_1 curl -I <URL>
   ```

2. Для localhost использовать `host.docker.internal`:
   ```bash
   ./shannon start URL=http://host.docker.internal:3000 REPO=/path/to/repo
   ```

3. Убедиться, что приложение запущено и доступно

### Проблема 4: Pre-Recon не завершился

**Симптомы:**
- Workflow застрял на фазе `pre-recon`
- Ошибка валидации: `OutputValidationError`

**Решение:**
1. Проверить логи pre-recon:
   ```bash
   ./shannon logs ID=<workflow-id>
   ```

2. Убедиться, что создан `code_analysis_deliverable.md`

3. Проверить доступ к репозиторию:
   ```bash
   docker exec shannon_worker_1 ls -la /target-repo
   ```

---

## 📝 Чеклист для Запуска Black Box

- [ ] Pre-Reconnaissance успешно завершен
- [ ] Создан `code_analysis_deliverable.md`
- [ ] Chromium установлен и доступен
- [ ] Playwright MCP доступен через npx
- [ ] Переменные окружения настроены
- [ ] Целевое приложение доступно
- [ ] Workflow перешел к фазе Reconnaissance
- [ ] MCP серверы подключены (видно в логах)
- [ ] AI агент использует Playwright инструменты

---

## 🎯 Итог

**Black box тестирование должно работать автоматически**, если:

1. ✅ **Pre-Reconnaissance завершен** - создан `code_analysis_deliverable.md`
2. ✅ **Chromium установлен** - уже есть в контейнере
3. ✅ **Playwright MCP доступен** - устанавливается через npx автоматически
4. ✅ **Приложение доступно** - URL отвечает на запросы

**Никаких дополнительных действий не требуется!** Black box тестирование запускается автоматически после Pre-Reconnaissance.

---

## 🔗 Связанные Документы

- [WHITEBOX_ANALYSIS.md](./WHITEBOX_ANALYSIS.md) - White box тестирование
- [QUICK_START.md](./QUICK_START.md) - Быстрый старт
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Руководство по развертыванию

