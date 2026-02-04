# White Box Тестирование в Shannon - Точки Входа

## 📋 Краткое Резюме

White box тестирование в Shannon начинается с **фазы Pre-Reconnaissance**, которая является первой фазой workflow и выполняет статический анализ исходного кода.

---

## 🎯 Основные Точки Входа

### 1. **Workflow Entry Point** - Начало выполнения
**Файл:** `src/temporal/workflows.ts`
**Строки:** ~120-130

```typescript
// === Phase 1: Pre-Reconnaissance ===
state.currentPhase = 'pre-recon';
state.currentAgent = 'pre-recon';
await a.logPhaseTransition(activityInput, 'pre-recon', 'start');
state.agentMetrics['pre-recon'] = await a.runPreReconAgent(activityInput);
```

**Описание:** Это первая фаза workflow, которая запускается автоматически при старте пентеста.

---

### 2. **Activity Entry Point** - Выполнение агента
**Файл:** `src/temporal/activities.ts`
**Функция:** `runPreReconAgent()`
**Строки:** ~400-450 (примерно)

**Описание:** Temporal activity, которая вызывает функцию pre-recon из phases.

---

### 3. **Pre-Recon Phase** - Основная логика анализа кода
**Файл:** `src/phases/pre-recon.ts`
**Функция:** `runPreReconPhase()`
**Строки:** ~350-380

```typescript
export async function runPreReconPhase(
  webUrl: string,
  sourceDir: string,
  variables: PromptVariables,
  config: DistributedConfig | null,
  pipelineTestingMode: boolean,
  sessionId: string | null,
  outputPath?: string
): Promise<PreReconResult>
```

**Описание:** Главная функция фазы pre-recon, которая координирует анализ кода.

---

### 4. **Wave 1 - Code Analysis Agent** - AI анализ кода
**Файл:** `src/phases/pre-recon.ts`
**Функция:** `runPreReconWave1()`
**Строки:** ~142-210

**Ключевые моменты:**
- Загружает промпт `'pre-recon-code'`
- Вызывает AI агента для анализа исходного кода
- Сохраняет результат в `deliverables/code_analysis_deliverable.md`

```typescript
const codeAnalysisResult = await runClaudePromptWithRetry(
  await loadPrompt('pre-recon-code', variables, null, pipelineTestingMode),
  sourceDir,
  AGENTS['pre-recon'].displayName,
  'pre-recon',
  // ...
);
```

---

### 5. **AI Executor** - Выполнение AI запроса
**Файл:** `src/ai/claude-executor.ts`
**Функция:** `runClaudePrompt()`
**Строки:** ~200-300

**Описание:** Низкоуровневая функция, которая выполняет запрос к Claude API с доступом к исходному коду через MCP сервер.

**Ключевые моменты:**
- Настраивает MCP серверы для доступа к файловой системе
- Использует `shannon-helper` MCP сервер для чтения файлов
- Передает `sourceDir` (repoPath) для доступа к коду

---

### 6. **Prompt Loading** - Загрузка промпта для анализа
**Файл:** `src/prompts/prompt-manager.ts`
**Функция:** `loadPrompt()`
**Промпт:** `prompts/pre-recon-code.txt`

**Описание:** Загружает промпт, который инструктирует AI анализировать исходный код.

**Ключевые части промпта:**
- Роль: Principal Engineer специализирующийся на security-focused code review
- Задача: Анализ исходного кода для генерации security-relevant архитектурного summary
- Выход: `deliverables/code_analysis_deliverable.md`

---

### 7. **MCP Server - File Access** - Доступ к файлам
**Файл:** `mcp-server/src/index.ts`
**Сервер:** `shannon-helper`

**Описание:** MCP сервер предоставляет инструменты для чтения файлов из репозитория.

**Инструменты:**
- `read_file` - чтение файлов
- `list_directory` - список директорий
- `search_code` - поиск по коду

---

## 🔄 Поток Выполнения White Box Анализа

```
1. workflows.ts:pentestPipelineWorkflow()
   └─> runPreReconAgent(activityInput)
       │
2. activities.ts:runPreReconAgent()
   └─> runPreReconPhase(...)
       │
3. phases/pre-recon.ts:runPreReconPhase()
   └─> runPreReconWave1()
       │
4. phases/pre-recon.ts:runPreReconWave1()
   └─> loadPrompt('pre-recon-code', ...)
   └─> runClaudePromptWithRetry(...)
       │
5. ai/claude-executor.ts:runClaudePrompt()
   └─> buildMcpServers(sourceDir, agentName)
   └─> query() [Claude SDK]
       │
6. Claude AI Agent
   └─> Использует MCP инструменты для чтения кода
   └─> Анализирует исходный код
   └─> Сохраняет результат через save_deliverable
       │
7. Результат сохраняется в:
   deliverables/code_analysis_deliverable.md
```

---

## 📁 Ключевые Файлы

### Основные файлы для white box тестирования:

1. **`src/temporal/workflows.ts`**
   - Определяет порядок выполнения фаз
   - Запускает pre-recon как первую фазу

2. **`src/temporal/activities.ts`**
   - `runPreReconAgent()` - activity для pre-recon
   - `runAgentActivity()` - общая логика выполнения агентов

3. **`src/phases/pre-recon.ts`**
   - `runPreReconPhase()` - главная функция фазы
   - `runPreReconWave1()` - первая волна (AI анализ кода)
   - `runPreReconWave2()` - вторая волна (инструменты)

4. **`src/ai/claude-executor.ts`**
   - `runClaudePrompt()` - выполнение AI запросов
   - `buildMcpServers()` - настройка доступа к файлам
   - `validateAgentOutput()` - валидация результатов

5. **`src/prompts/prompt-manager.ts`**
   - `loadPrompt()` - загрузка промптов
   - Подстановка переменных (REPO_PATH, WEB_URL)

6. **`prompts/pre-recon-code.txt`**
   - Промпт для AI агента
   - Инструкции по анализу кода

7. **`mcp-server/src/index.ts`**
   - MCP сервер для доступа к файлам
   - Инструменты для чтения кода

8. **`src/constants.ts`**
   - Определение агентов
   - Валидаторы для проверки результатов

---

## 🔍 Где Передается REPO_PATH

### 1. Входная точка
**Файл:** `src/temporal/client.ts`
- CLI принимает `REPO` параметр
- Преобразуется в `repoPath` в `ActivityInput`

### 2. Передача через workflow
**Файл:** `src/temporal/workflows.ts`
```typescript
const activityInput: ActivityInput = {
  webUrl: input.webUrl,
  repoPath: input.repoPath,  // <-- Здесь
  workflowId,
  // ...
};
```

### 3. Использование в pre-recon
**Файл:** `src/phases/pre-recon.ts`
```typescript
const variables: PromptVariables = {
  webUrl,
  repoPath: sourceDir,  // <-- Используется как sourceDir
};
```

### 4. Передача в AI executor
**Файл:** `src/ai/claude-executor.ts`
```typescript
buildMcpServers(sourceDir, agentName)  // <-- sourceDir = repoPath
```

---

## 🎯 Ключевые Моменты

1. **White box анализ начинается СРАЗУ** при запуске workflow в фазе Pre-Reconnaissance
2. **Единственный агент с полным доступом к коду** - `pre-recon-code`
3. **Результат анализа** сохраняется в `deliverables/code_analysis_deliverable.md`
4. **Доступ к коду** через MCP сервер `shannon-helper`
5. **Все последующие агенты** используют результаты pre-recon для фокусировки

---

## 📝 Важные Замечания

- Pre-recon выполняется **ПОСЛЕДОВАТЕЛЬНО** (не параллельно)
- Это **ПЕРВАЯ** фаза в workflow
- Результат анализа кода используется всеми последующими агентами
- Если pre-recon не найдет компоненты безопасности, они не будут протестированы

---

## 🔗 Связи с Другими Фазами

- **Pre-Recon** → создает `code_analysis_deliverable.md`
- **Recon** → использует результаты pre-recon для приоритизации
- **Vuln Analysis** → использует архитектурный анализ для поиска уязвимостей
- **Exploitation** → использует информацию о компонентах для атак
- **Reporting** → использует все данные для финального отчета

