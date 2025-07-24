🇬🇧🇺🇸ENG
---
🤖 # Console AI Chat using g4f v1.1.1

[![Code Version](https://img.shields.io/badge/G4FChat-1.1.1-blue.svg)]
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![g4f Version](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🎉 Release 1.1.1 Announcement

We're excited to announce version 1.1.1 of G4FChat! This update brings significant improvements and new features to enhance your AI chatting experience.

### 🔥 What's New

- **Enhanced Model Support**: Added 20+ new cutting-edge models including:
  - Claude 3.5 Sonnet
  - Gemini 2.5 Flash/Pro
  - Llama 3.1/3.2 series
  - Qwen 2.5/3 models
  - DeepSeek V3/R1

- **Improved Model Organization**: 
  - Models are now logically grouped by provider (OpenAI, Anthropic, Google, etc.)
  - Better model discovery with `/models` command
  - More accurate model suggestions when using `/setmodel`

- **Critical Bug Fixes**:
  - Fixed provider selection algorithm
  - Resolved chat history saving issues
  - Improved error handling and recovery
  - Fixed model switching reliability

- **User Experience Improvements**:
  - Better command feedback with helpful suggestions
  - Enhanced status information in `/status` command
  - More reliable code block saving
  - Improved multi-language support

### 🚀 Getting Started

Update your existing installation:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

Or install fresh:
```bash
git clone https://github.com/AITechnologyDev/G4FChat.git
cd G4FChat
pip install -r requirements.txt
python G4FChat.py
```

### 📌 Known Issues

- Some models may have limited availability depending on provider status
- First-time initialization might take longer due to enhanced provider checks

## 🛠 Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `/newchat`     | Create a new chat                    |
| `/usechat <id>`| Switch to specific chat              |
| `/delchat <id>`| Delete chat                          |
| `/chats`       | Show chat list                       |
| `/setmodel <name>`| Set AI model                      |
| `/mymodel`     | Show current model                   |
| `/models`      | Show available models                |
| `/providers`   | Show active providers                |
| `/status`      | Show system status                   |
| `/lang <en/ru>`| Switch language (English/Russian)    |
| `/stats`       | Show usage statistics                |
| `/exit`        | Exit program                         |
| `/help`        | Show help                            |

## 📂 File structure

```
G4FChat/
├── G4FChat.py         # Main script
├── saved_code/        # Auto-saved code snippets
├── user_models.json   # Saved user models
├── user_chats.json    # Saved chat histories
├── user_lang.json     # User language preferences
├── ai_chat.log        # Log file
└── requirements.txt   # Dependencies
```

## 🌟 Key Features

- **Auto-save**: All settings and chats are automatically saved
- **Code preservation**: Code blocks automatically saved with clickable links
- **Multi-language**: Full English/Russian interface support
- **Theming**: Customize colors through Rich styling
- **Error resilience**: Automatic provider fallback system

## 🐛 Debugging

Logs are saved to `ai_chat.log`:
```bash
tail -f ai_chat.log
```

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
---
> Developed by [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025

---
🇷🇺RU
---
🤖 # Консольный AI Чат с использованием g4f v1.1.1

[![Версия кода](https://img.shields.io/badge/G4FChat-1.1.1-blue.svg)]
[![Версия Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Версия g4f](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![Лицензия](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

## 🎉 Анонс версии 1.1.1

Мы рады представить версию 1.1.1 G4FChat! Это обновление приносит значительные улучшения и новые функции для улучшения вашего общения с ИИ.

### 🔥 Что нового

- **Расширенная поддержка моделей**: Добавлено 20+ новых современных моделей, включая:
  - Claude 3.5 Sonnet
  - Gemini 2.5 Flash/Pro
  - Llama 3.1/3.2 серии
  - Qwen 2.5/3 модели
  - DeepSeek V3/R1

- **Улучшенная организация моделей**:
  - Модели теперь сгруппированы по провайдерам (OpenAI, Anthropic, Google и др.)
  - Улучшенный поиск моделей через команду `/models`
  - Более точные подсказки при использовании `/setmodel`

- **Исправления ошибок**:
  - Улучшен алгоритм выбора провайдеров
  - Исправлены проблемы с сохранением истории чатов
  - Улучшена обработка ошибок
  - Повышена надежность переключения моделей

- **Улучшения пользовательского опыта**:
  - Более информативные ответы на команды
  - Улучшенная информация в команде `/status`
  - Более надежное сохранение блоков кода
  - Улучшена поддержка нескольких языков

### 🚀 Начало работы

Обновите существующую установку:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

Или установите заново:
```bash
git clone https://github.com/AITechnologyDev/G4FChat.git
cd G4FChat
pip install -r requirements.txt
python G4FChat.py
```

### 📌 Известные проблемы

- Некоторые модели могут иметь ограниченную доступность в зависимости от статуса провайдеров
- Первоначальная инициализация может занимать больше времени из-за улучшенных проверок

## 🛠 Команды

| Команда         | Описание                          |
|-----------------|-----------------------------------|
| `/newchat`      | Создать новый чат                 |
| `/usechat <id>` | Переключиться на чат              |
| `/delchat <id>` | Удалить чат                       |
| `/chats`        | Показать список чатов             |
| `/setmodel <name>`| Установить модель ИИ            |
| `/mymodel`      | Показать текущую модель           |
| `/models`       | Показать доступные модели         |
| `/providers`    | Показать активные провайдеры      |
| `/status`       | Показать статус системы           |
| `/lang <en/ru>` | Переключить язык (Англ/Рус)       |
| `/stats`        | Показать статистику использования |
| `/exit`         | Выйти из программы                |
| `/help`         | Показать справку по командам      |

## 📂 Структура файлов

```
G4FChat/
├── G4FChat.py         # Основной скрипт
├── saved_code/        # Автосохранённые фрагменты кода
├── user_models.json   # Сохранённые модели пользователей
├── user_chats.json    # Сохранённые истории чатов
├── user_lang.json     # Языковые настройки пользователей
├── ai_chat.log        # Файл логов
└── requirements.txt   # Зависимости
```

## 🌟 Основные возможности

- **Автосохранение**: Все настройки и чаты сохраняются автоматически
- **Сохранение кода**: Блоки кода сохраняются с кликабельными ссылками
- **Многоязычность**: Полная поддержка Английского и Русского интерфейсов
- **Темы оформления**: Настройка цветов через стили Rich
- **Устойчивость к ошибкам**: Автоматический переход на рабочие провайдеры

## 🐛 Отладка

Логи сохраняются в файл `ai_chat.log`:
```bash
tail -f ai_chat.log
```

## 📜 Лицензия

Этот проект распространяется под лицензией MIT - подробности см. в файле [LICENSE](LICENSE).

---
> Разработано [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025
```

Проект полностью готов к использованию! Для запуска просто выполните:

```bash
python G4FChat.py
```