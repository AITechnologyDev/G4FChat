🇬🇧🇺🇸ENG
---
🤖 # Console AI Chat using g4f

[![Code Version](https://img.shields.io/badge/G4FChat-1.1.0-blue.svg)]
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![g4f Version](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A simple yet powerful console AI chatbot that uses the g4f library to interact with different language models through free APIs.

## ✨ Features

- Support for 50+ models (GPT-4o, Claude 3.5, Llama 3, Gemini, etc.)
- Manage multiple chats with history saving
- Beautiful interface with Rich library
- Automatic detection of working providers
- Syntax highlighting for code blocks
- Model "thinking" reflections system
- Cross-platform support (Windows/Linux/macOS/Termux)
- Multi-language interface (English/Russian)
- Auto-saving of code snippets
- Usage statistics tracking

## 🆕 New in 1.1.0

- **Multi-language support**: Switch between English/Russian with `/lang` command
- **Code auto-saving**: Code blocks automatically saved to `saved_code/` folder
- **Enhanced UI**: Improved panels and progress indicators
- **Statistics**: Track usage with `/stats` command
- **Optimizations**: Faster provider initialization

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/AITechnologyDev/G4FChat.git
cd G4FChat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Launching
```bash
python G4FChat.py
```

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
🇷🇺 RU
---
# 🤖 Консольный AI Чат с использованием g4f

[![Версия кода](https://img.shields.io/badge/G4FChat-1.1.0-blue.svg)]
[![Версия Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Версия g4f](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![Лицензия](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Простой, но мощный консольный AI чат-бот, использующий библиотеку g4f для взаимодействия с различными языковыми моделями через бесплатные API.

## ✨ Особенности

- Поддержка 50+ моделей (GPT-4o, Claude 3.5, Llama 3, Gemini и др.)
- Управление несколькими чатами с сохранением истории
- Красивый интерфейс с библиотекой Rich
- Автоматическое определение рабочих провайдеров
- Подсветка синтаксиса для блоков кода
- Система "размышлений" модели
- Кроссплатформенная работа (Windows/Linux/macOS/Termux)
- Многоязычный интерфейс (Английский/Русский)
- Автосохранение фрагментов кода
- Отслеживание статистики использования

## 🆕 Новое в 1.1.0

- **Поддержка языков**: Переключение между Английским/Русским командой `/lang`
- **Автосохранение кода**: Блоки кода автоматически сохраняются в папку `saved_code/`
- **Улучшенный интерфейс**: Оптимизированные панели и индикаторы прогресса
- **Статистика**: Отслеживание использования командой `/stats`
- **Оптимизации**: Ускоренная инициализация провайдеров

## ⚙️ Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/AITechnologyDev/G4FChat.git
cd G4FChat
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## 🚀 Запуск
```bash
python G4FChat.py
```

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
