🇬🇧🇺🇸ENG
---
🤖 # Console AI Chat using g4f

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![g4f Version](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

A simple yet powerful console AI chatbot that uses the g4f library to interact with different language models through free APIs.

## ✨ Features

- Support for 50+ models (GPT-4o, Claude 3.5, Llama 3, Gemini, etc.)
- Manage multiple chats
- Saving message history
- Beautiful interface with Rich
- Automatic detection of a working provider
- Markdown syntax highlighting
- The system of "thinking" of the model
- Cross-platform work (Windows/Linux/macOS/Termux)

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
python G4FENGChat.py
```

## 🛠 Command

| Team       | Description                          |
|---------------|-----------------------------------|
| `/newchat`    | Create a new chat                 |
| `/usechat <id>`| Switch to chat             |
| `/delchat <id>`| Delete Chat                      |
| `/chats`      | Show chat list             |
| `/setmodel <name>`| Install Model              |
| `/mymodel`    | Show Current Model           |
| `/models`     | Show available models         |
| `/providers`  | Show Active Providers      |
| `/status`     | Show system status           |
| `/exit`       | Log out of the program                |
| `/help`       | Show command help      |

## 📂 File structure

```
G4FChat/
├── G4FENGChat.py # Main Script
├── user_models.json # Saved user models
├── user_chats.json # Saved user chats
├── ai_chat.log # Log File
└── requirements.txt # Dependencies
```

## 🌟 Features of use

- **Autosave**: All chats and settings are automatically saved
- **History**: Supports the history
- **Themes**: Can easily customize the color scheme via Rich

## 🐛 Debugging

Logs are saved to a file `ai_chat.log`:
```bash
tail -f ai_chat.log
```

## 📜 License

This project is licensed under the MIT License—see [LICENSE] for details.
---
> Developed [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025

---
🇷🇺 RU
---
# 🤖 Консольный AI Чат с использованием g4f

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![g4f Version](https://img.shields.io/badge/g4f-0.5.7.5-green.svg)](https://github.com/xtekky/gpt4free)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

Простой, но мощный консольный AI чат-бот, использующий библиотеку g4f для взаимодействия с различными языковыми моделями через бесплатные API.

## ✨ Особенности

- Поддержка 50+ моделей (GPT-4o, Claude 3.5, Llama 3, Gemini и др.)
- Управление несколькими чатами
- Сохранение истории сообщений
- Красивый интерфейс с помощью Rich
- Автоматическое определение рабочего провайдера
- Подсветка синтаксиса Markdown
- Система "размышлений" модели
- Кроссплатформенная работа (Windows/Linux/macOS/Termux)

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
python G4FRUChat.py
```

## 🛠 Команды

| Команда       | Описание                          |
|---------------|-----------------------------------|
| `/newchat`    | Создать новый чат                 |
| `/usechat <id>`| Переключиться на чат             |
| `/delchat <id>`| Удалить чат                      |
| `/chats`      | Показать список чатов             |
| `/setmodel <name>`| Установить модель              |
| `/mymodel`    | Показать текущую модель           |
| `/models`     | Показать доступные модели         |
| `/providers`  | Показать активные провайдеры      |
| `/status`     | Показать статус системы           |
| `/exit`       | Выйти из программы                |
| `/help`       | Показать справку по командам      |

## 📂 Структура файлов

```
G4FChat/
├── G4FRUChat.py        # Основной скрипт
├── user_models.json  # Сохраненные модели пользователей
├── user_chats.json   # Сохраненные чаты пользователей
├── ai_chat.log       # Файл логов
└── requirements.txt  # Зависимости
```

## 🌟 Особенности использования

- **Автосохранение**: Все чаты и настройки автоматически сохраняются
- **Блоки кода**: Код автоматически сохраняется в папку `saved_code`
- **История**: Поддерживается история
- **Темы**: Можно легко настроить цветовую схему через Rich

## 🐛 Отладка

Логи сохраняются в файл `ai_chat.log`:
```bash
tail -f ai_chat.log
```

## 📜 Лицензия

Этот проект распространяется под лицензией MIT - подробности см. в файле [LICENSE](LICENSE).

---
> Разработано [AiTechnologyDev](https://github.com/AITechnologyDev) | 2025