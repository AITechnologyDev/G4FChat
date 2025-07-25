🇬🇧🇺🇸ENG
---
# 🤖 Console AI Chat using g4f

[
![G4FChat Version](https://img.shields.io/badge/G4FChat-1.1.2-blue.svg)
]
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![G4F Library](https://img.shields.io/badge/g4f-latest-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

🎉 **Release 1.1.2 Announcement**

We're excited to announce version 1.1.2 of G4FChat! This update builds upon previous versions, incorporating expanded model support, refined provider handling, and improved stability.

🔥 **What's New in 1.1.2**

*   **Significantly Expanded Model Support**: Added numerous new models and variants across various providers, including newer OpenAI (`gpt-4o-*`, `o1-*`), Claude (`claude-3.5-sonnet`, `claude-3.7-sonnet`), Qwen (`qwen-3-*`, `qwen-2.5-*`), Llama (`llama-3.2-*`, `llama-3.3-*`), Mistral, and specialized reasoning models. The `/models` command now lists a comprehensive selection.
*   **Enhanced Provider Management**: Improved provider initialization logic with safer attribute checking (`getattr(provider, 'working', True)`) and refined blacklists/backup lists for better reliability.
*   **Improved Error Handling & Fallbacks**: Added specific handling for timeouts and empty responses during generation, providing clearer feedback in the UI (`timeout_error`, `no_response_error`).
*   **Client API Compatibility Check**: The script now checks for and can utilize the newer `g4f.client.Client` API if available, falling back to the legacy API otherwise, displaying the current mode in the UI (`using_client_api`, `using_legacy_api`).
*   **UI/UX Refinements**: Minor adjustments to command feedback and status information for clarity.

🚀 **Getting Started**

1.  **Clone or Update:**
    *   **Update existing:**
        ```bash
        git pull origin main
        pip install -r requirements.txt --upgrade
        ```
    *   **Fresh install:**
        ```bash
        git clone https://github.com/AITechnologyDev/G4FChat.git
        cd G4FChat
        pip install -r requirements.txt
        ```
2.  **Run the Script:**
    ```bash
    python G4FChat.py
    ```

📌 **Known Issues**

*   Some newly added models may have limited availability depending on provider status or `g4f` compatibility.
*   First-time initialization might take slightly longer due to enhanced provider checks.
*   Model availability and performance can vary based on external factors affecting `g4f` providers.

🛠 **Commands**

| Command              | Description                 |
| -------------------- | --------------------------- |
| `/newchat`           | Create a new chat           |
| `/usechat <id>`      | Switch to specific chat     |
| `/delchat <id>`      | Delete chat                 |
| `/chats`             | Show chat list              |
| `/setmodel <name>`   | Set AI model                |
| `/mymodel`           | Show current model          |
| `/models`            | Show available models       |
| `/providers`         | Show active providers       |
| `/status`            | Show system status          |
| `/lang <en/ru>`      | Switch language (Eng/Rus)   |
| `/stats`             | Show usage statistics       |
| `/exit`              | Exit program                |
| `/help`              | Show help                   |

📂 **File structure**

```
G4FChat/
├── G4FChat.py         # Main script
├── chat_config/       # Directory for saved data
│   ├── saved_code/    # Auto-saved code snippets
│   ├── user_models.json  # Saved user models
│   ├── user_chats.json   # Saved chat histories
│   └── user_lang.json    # User language preferences
├── ai_chat.log        # Log file
└── requirements.txt   # Dependencies
```
*(Note: Configuration files are now saved in the `chat_config` subdirectory)*

🌟 **Key Features**

*   **Auto-save**: All settings, chats, and language preferences are automatically saved in the `chat_config` directory.
*   **Code preservation**: Code blocks from AI responses are automatically saved to `chat_config/saved_code/` with clickable links in the terminal.
*   **Multi-language**: Full English/Russian interface support. Easily switch using `/lang`.
*   **Theming**: Leverages Rich library for enhanced terminal output and styling.
*   **Error resilience**: Features an automatic provider fallback system to attempt different providers if one fails or times out.
*   **Model Thinking Visualization**: If supported by the model's output format, displays reasoning steps (`<thinking>`, `[reasoning]`, `<analysis>`) in a structured way.

🐛 **Debugging**

Logs are saved to `ai_chat.log`. Monitor them for detailed information:
```bash
tail -f ai_chat.log
# Or, if logs are in the chat_config directory:
tail -f chat_config/ai_chat.log
```

📜 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed by [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025

### Key Changes Made:

1.  **Version Bump:** Updated version references to `1.1.2`.
2.  **Feature Highlights:** Reworded the "What's New" section to emphasize the expanded models, improved provider logic, error handling, and Client API compatibility.
3.  **File Structure:** Corrected the file structure to reflect that config files (including logs and saved code) are now placed inside the `chat_config` directory, as per the script.
4.  **Clarifications:** Added notes about potential model availability issues and clarified the location of the log file based on the script's configuration.
5.  **Minor Wording:** Adjusted some descriptions for clarity and consistency.

---
🇷🇺RU
---
# 🤖 Консольный искусственный интеллект-чат с использованием g4f

[
![Версия G4FChat](https://img.shields.io/badge/G4FChat-1.1.2-blue.svg)
]
![Версия на Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Библиотека G4F](https://img.shields.io/badge/g4f-latest-green.svg)
![Лицензия](https://img.shields.io/badge/license-MIT-yellow.svg)

🎉 ** Анонс релиза 1.1.2**

Мы рады объявить о выпуске версии 1.1.2 G4FChat! Это обновление основано на предыдущих версиях и включает расширенную поддержку моделей, улучшенную работу с поставщиками и улучшенную стабильность.

🔥 ** Что нового в версии 1.1.2**

* ** Значительно расширена поддержка моделей **: Добавлено множество новых моделей и вариантов для различных поставщиков, включая более новые OpenAI ("gpt-4o-*", "o1-*"), Claude ("claude-3.5-sonnet", "claude-3.7-sonnet"), Qwen (`qwen-3-*`, "qwen-2.5-*"), Llama ("llama-3.2-*", "llama-3.3-*"), Mistral и специализированные модели мышления. Команда "/models" теперь отображает полный список выбранных поставщиков.
* ** Улучшенное управление поставщиками **: Улучшена логика инициализации поставщиков с более безопасной проверкой атрибутов ("getattr(поставщик, "рабочий", True)") и улучшены черные списки /списки резервных копий для повышения надежности.
* ** Улучшена обработка ошибок и резервные варианты **: Добавлена специальная обработка тайм-аутов и пустых ответов во время генерации, что обеспечивает более четкую обратную связь в пользовательском интерфейсе (`timeout_error`, `no_response_error`).
* ** Проверка совместимости клиентского API **: Скрипт теперь проверяет наличие и может использовать более новый g4f.client.Клиентский API, если он доступен, в противном случае возвращается к устаревшему API, отображая текущий режим в пользовательском интерфейсе (`using_client_api`, `using_legacy_api`).
* ** Доработки пользовательского интерфейса / UX **: Небольшие изменения в обратной связи с командой и информации о статусе для большей ясности.

🚀 **Начало работы**

1. ** Клонировать или обновить:**
    * ** Обновить существующий:**
        ``bash
git pull origin main
        установка pip -r requirements.txt --обновление
        ```
    * ** Новая установка:**
        ``bash
git clone https://github.com/AITechnologyDev/G4FChat.git
        cd G4FChat
pip install -r requirements.txt
        ```
2. **Запустите скрипт:**
    ``bash
python G4FChat.py
    ```

📌 **Известные проблемы**

* Доступность некоторых недавно добавленных моделей может быть ограничена в зависимости от статуса поставщика или совместимости с g4f.
* Инициализация при первом запуске может занять немного больше времени из-за расширенной проверки поставщика.
* Доступность и производительность модели могут варьироваться в зависимости от внешних факторов, влияющих на поставщиков услуг g4f.

🛠 **Команды**

| Команда | Описание |
| -------------------- | --------------------------- |
| `/новый чат`           | Создать новый чат |
| `/usechat <id>` | Переключиться на определенный чат |
| `/delchat <id>` | Удалить чат |
| "/чаты" | Показать список чатов |
| `/setmodel <имя>` | Установить модель искусственного интеллекта |
| `/mymodel` | Показать текущую модель |
| `/модели`            | Показать доступные модели |
| `/поставщики` | Показать активных поставщиков |
| `/статус`            | Показать состояние системы |
| `/lang <en/ru>` | Переключить язык (Eng/Rus) |
| `/stats` | Показать статистику использования |
| `/exit`              | Выйти из программы |
| "/help" | Показать справку |

📂 **Файловая структура**

```
G4FChat/
├── G4FChat.py # Основной скрипт
├── chat_config/ # Каталог для сохраненных данных
│ ├── сохраненный код / # Автоматически сохраняемые фрагменты кода
│ ├── модели пользователей.json # Сохраненные модели пользователей
│ ├── user_chats.json # Сохраненные истории чатов
│ └── user_lang.json # Языковые настройки пользователя
├── ai_chat.журнал # Файл журнала
└── requirements.txt # Зависимости
```
* (Примечание: Файлы конфигурации теперь сохраняются в подкаталоге "chat_config")*

🌟 **Основные возможности**

* ** Автоматическое сохранение **: Все настройки, чаты и языковые предпочтения автоматически сохраняются в каталоге "chat_config".
* **Сохранение кода**: Блоки кода из ответов искусственного интеллекта автоматически сохраняются в "chat_config/saved_code/" с интерактивными ссылками в терминале.
* ** Многоязычность **: Полная поддержка интерфейса на английском и русском языках. Простое переключение с помощью "/lang".
* ** Тематизация **: Использует богатую библиотеку для улучшения вывода данных на терминал и оформления.
* ** Устойчивость к ошибкам **: Поддерживает автоматическую резервную систему, позволяющую обращаться к другим поставщикам в случае сбоя или истечения времени ожидания.
* ** Визуализация мышления модели**: Если поддерживается формат вывода модели, отображает этапы рассуждения ("<мышление>", "[рассуждение]", "<анализ>") в структурированном виде.

🐛 **Отладка**

Журналы сохраняются в "ai_chat.log". Следите за ними для получения подробной информации:
``bash
tail -f ai_chat.log
# Или, если журналы находятся в каталоге chat_config:
tail -f chat_config/ai_chat.log
```

📜 **Лицензия**

Этот проект лицензирован по лицензии MIT - подробности смотрите в файле [LICENSE] (ЛИЦЕНЗИЯ).

---

Разработан компанией [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025

### Внесены основные изменения:

1. ** Изменение версии:** Обновленная версия ссылается на "1.1.2".
2. ** Основные функции: ** Переработан раздел "Что нового", чтобы подчеркнуть расширенные модели, улучшенную логику провайдера, обработку ошибок и совместимость клиентского API.
3. ** Файловая структура: ** Исправлена файловая структура, чтобы отразить, что конфигурационные файлы (включая логи и сохраненный код) теперь размещаются в каталоге "chat_config" в соответствии со сценарием.
4. **Уточнения:** Добавлены примечания о возможных проблемах с доступностью модели и уточнено расположение файла журнала в зависимости от конфигурации скрипта.
5. ** Незначительные изменения:** Исправлены некоторые описания для большей ясности и последовательности.