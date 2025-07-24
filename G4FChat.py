import uuid
import g4f
import json
import logging
import sys
import time
import inspect
import threading
import os
import re
from threading import Lock, Event
from g4f import Provider
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.style import Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import TerminalFormatter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_chat.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# Инициализация Rich
console = Console()
error_style = Style(color="red", bold=True)
success_style = Style(color="green", bold=True)
warning_style = Style(color="yellow", bold=True)
info_style = Style(color="blue", bold=True)
ai_style = Style(color="cyan", bold=True)
code_style = Style(color="magenta")

# Конфигурационные файлы
MODEL_FILE = 'user_models.json'
USER_CHATS_FILE = 'user_chats.json'
LANG_FILE = 'user_lang.json'

# Кэширование данных
user_models_cache = {}
user_chats_cache = {}
user_lang_cache = {}
active_providers = []
provider_classes = {}
stats = {
    'total_messages': 0,
    'saved_code_blocks': 0,
    'active_chats': 0,
    'last_activity': time.time()
}

# Глобальная блокировка для потокобезопасности
cache_lock = Lock()

# Черный список провайдеров
BLACKLISTED_PROVIDERS = ['BlackForestLabs_Flux1Dev', 'DeepInfra', 'FlowGpt', 'Free2GPT', 'ImageLabs', 'HuggingFace', 'PollinationsImage']

# Словари перевода
TRANSLATIONS = {
    'en': {
        'welcome_menu': "Welcome",
        'welcome': "Console AI Chat",
        'developer': "Developer",
        'github': "GitHub",
        'help_title': "Help",
        'commands': "Commands",
        'new_chat': "Create new chat",
        'switch_chat': "Switch chat",
        'delete_chat': "Delete chat",
        'list_chats': "Show chat list",
        'set_model': "Set model",
        'current_model': "Current model",
        'list_models': "Show available models",
        'list_providers': "Show active providers",
        'system_status': "System status",
        'exit': "Exit program",
        'help': "Show help",
        'lang': "Set language",
        'stats': "Show usage stats",
        'chat_prompt': "You",
        'start_chat': "Just type a message or question",
        'ai_prompt': "AI",
        'thinking': "Model reflections",
        'saving_code': "Saved code blocks",
        'generating': "Generating response...",
        'model_set': "Model set",
        'model_error': "Model not available",
        'chat_created': "New chat created and selected",
        'chat_switched': "Switched to chat",
        'chat_not_found': "Chat not found",
        'chat_deleted': "Chat deleted",
        'no_chats': "You have no chats yet",
        'your_chats': "Your Chats",
        'current_model_title': "Current Model",
        'available_models': "Available models",
        'active_providers': "Active providers",
        'system_status_title': "System status",
        'exit_confirmation': "Exiting program...",
        'unknown_command': "Unknown command",
        'gen_error': "Response generation error",
        'main_error': "An error occurred. Continuing...",
        'code_saved': "Saved {} code block(s)",
        'stats_title': "Usage Statistics",
        'total_messages': "Total messages",
        'saved_blocks': "Saved code blocks",
        'active_chats': "Active chats",
        'last_activity': "Last activity",
        'time_format': "%Y-%m-%d %H:%M",
        'lang_set': "Language set",
        'invalid_lang': "Invalid language. Use 'en' or 'ru'",
        'providers_title': "Active Providers",
        'total_providers': "Total providers",
        'saved_code_location': "Code saved to:"
    },
    'ru': {
        'welcome_menu': "Добро пожаловать",
        'welcome': "Консольный AI Чат",
        'developer': "Разработчик",
        'github': "GitHub",
        'help_title': "Помощь",
        'commands': "Команды",
        'new_chat': "Создать новый чат",
        'switch_chat': "Переключить чат",
        'delete_chat': "Удалить чат",
        'list_chats': "Показать список чатов",
        'set_model': "Установить модель",
        'current_model': "Текущая модель",
        'list_models': "Показать доступные модели",
        'list_providers': "Показать активные провайдеры",
        'system_status': "Статус системы",
        'exit': "Выйти из программы",
        'help': "Показать справку",
        'lang': "Установить язык",
        'stats': "Показать статистику",
        'chat_prompt': "Вы",
        'start_chat': "Просто введите сообщение или вопрос",
        'ai_prompt': "ИИ",
        'thinking': "Размышления модели",
        'saving_code': "Сохраненные блоки кода",
        'generating': "Генерация ответа...",
        'model_set': "Модель установлена",
        'model_error': "Модель недоступна",
        'chat_created': "Новый чат создан и выбран",
        'chat_switched': "Переключено на чат",
        'chat_not_found': "Чат не найден",
        'chat_deleted': "Чат удален",
        'no_chats': "У вас пока нет чатов",
        'your_chats': "Ваши чаты",
        'current_model_title': "Текущая модель",
        'available_models': "Доступные модели",
        'active_providers': "Активные провайдеры",
        'system_status_title': "Статус системы",
        'exit_confirmation': "Выход из программы...",
        'unknown_command': "Неизвестная команда",
        'gen_error': "Ошибка генерации ответа",
        'main_error': "Произошла ошибка. Продолжаем...",
        'code_saved': "Сохранено блоков кода: {}",
        'stats_title': "Статистика использования",
        'total_messages': "Всего сообщений",
        'saved_blocks': "Сохранено блоков кода",
        'active_chats': "Активных чатов",
        'last_activity': "Последняя активность",
        'time_format': "%d.%m.%Y %H:%M",
        'lang_set': "Язык установлен",
        'invalid_lang': "Недопустимый язык. Используйте 'en' или 'ru'",
        'providers_title': "Активные провайдеры",
        'total_providers': "Всего провайдеров",
        'saved_code_location': "Код сохранён в:"
    }
}

def tr(key, lang='en'):
    """Получить перевод по ключу"""
    return TRANSLATIONS.get(lang, {}).get(key, key)

def get_user_lang(user_id):
    """Получить язык пользователя"""
    global user_lang_cache
    user_id = str(user_id)
    
    if not user_lang_cache:
        try:
            if os.path.exists(LANG_FILE):
                with open(LANG_FILE, 'r') as f:
                    user_lang_cache = json.load(f)
            else:
                user_lang_cache = {}
        except Exception as e:
            logger.error(f"Language load error: {e}")
            user_lang_cache = {}
    
    return user_lang_cache.get(user_id, 'en')

def save_user_lang(user_id, lang):
    """Сохранить язык пользователя"""
    global user_lang_cache
    user_id = str(user_id)
    
    with cache_lock:
        user_lang_cache[user_id] = lang
        try:
            with open(LANG_FILE, 'w') as f:
                json.dump(user_lang_cache, f)
        except Exception as e:
            logger.error(f"Error saving language: {e}")

# Получаем все доступные провайдеры автоматически
def get_all_providers():
    providers = []
    for name, obj in inspect.getmembers(g4f.Provider):
        if inspect.isclass(obj) and issubclass(obj, g4f.Provider.BaseProvider):
            providers.append(obj)
    return providers

# Инициализация провайдеров
def init_providers():
    global active_providers, provider_classes
    with cache_lock:
        if active_providers:
            return active_providers
            
        logger.info("Initializing providers...")
        with console.status("[bold blue]Initializing providers...[/]", spinner="dots"):
            all_providers = get_all_providers()
            active_providers = []
            provider_classes = {}
            
            for provider in all_providers:
                try:
                    provider_name = provider.__name__
                    
                    if provider_name in BLACKLISTED_PROVIDERS:
                        logger.info(f"Skipping blacklisted provider: {provider_name}")
                        continue
                    
                    if (hasattr(provider, 'working') and provider.working and 
                        (hasattr(provider, 'url') or hasattr(provider, 'model'))):
                        active_providers.append(provider)
                        provider_classes[provider_name] = provider
                        logger.info(f"Added provider: {provider_name}")
                except Exception as e:
                    logger.warning(f"Provider validation error {provider.__name__}: {str(e)[:100]}")
            
            if not active_providers:
                backup_providers = [g4f.Provider.You]
                for provider in backup_providers:
                    if provider.__name__ not in BLACKLISTED_PROVIDERS:
                        active_providers.append(provider)
                        provider_classes[provider.__name__] = provider
                logger.warning(f"Using backup providers: {[p.__name__ for p in active_providers]}")
            
            logger.info(f"Active providers: {len(active_providers)}")
        return active_providers

# Загрузка сохраненных моделей
def load_user_models():
    global user_models_cache
    with cache_lock:
        if user_models_cache:
            return user_models_cache
            
        try:
            if os.path.exists(MODEL_FILE):
                with open(MODEL_FILE, 'r') as f:
                    user_models_cache = json.load(f)
            else:
                user_models_cache = {}
        except Exception as e:
            logger.error(f"Model load error: {e}")
            user_models_cache = {}
        return user_models_cache

# Сохранение моделей
def save_user_models(data):
    global user_models_cache
    with cache_lock:
        user_models_cache = data
        try:
            with open(MODEL_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving models: {e}")

# Загрузка чатов
def load_user_chats():
    global user_chats_cache, stats
    with cache_lock:
        if user_chats_cache:
            return user_chats_cache
            
        try:
            if os.path.exists(USER_CHATS_FILE):
                with open(USER_CHATS_FILE, 'r', encoding='utf-8') as f:
                    user_chats_cache = json.load(f)
                    
                # Обновляем статистику
                stats['active_chats'] = 0
                for user_id, user_data in user_chats_cache.items():
                    chats = user_data.get("chats", {})
                    stats['active_chats'] += len(chats)
                    
                    for chat_id, chat_data in chats.items():
                        stats['total_messages'] += len(chat_data.get("history", []))
            else:
                user_chats_cache = {}
        except Exception as e:
            logger.error(f"Chat load error: {e}")
            user_chats_cache = {}
        return user_chats_cache

# Сохранение чатов
def save_user_chats(data):
    global user_chats_cache, stats
    with cache_lock:
        user_chats_cache = data
        
        # Обновляем статистику
        stats['active_chats'] = 0
        stats['total_messages'] = 0
        for user_id, user_data in data.items():
            chats = user_data.get("chats", {})
            stats['active_chats'] += len(chats)
            
            for chat_id, chat_data in chats.items():
                stats['total_messages'] += len(chat_data.get("history", []))
        
        stats['last_activity'] = time.time()
        
        try:
            with open(USER_CHATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving chats: {e}")

# Полный список моделей
def get_supported_models():
    return {
        "OpenAI": {
            'gpt-3.5-turbo',
            'gpt-4',
            'gpt-4o',
            'gpt-4o-mini',
            'gpt-4o-search',
            'gpt-4o-mini-search',
            'gpt-4-1',
            'gpt-4.1-mini',
            'gpt-4.1-nano',
            'gpt-4.5',
            'o1',
            'o1-mini',
            'o1-pro',
            'o3',
            'o3-mini',
            'o3-mini-high',
            'o4-mini',
            'o4-mini-high'
        },
        "Llama": {
            'llama-2-7b',
            'llama-2-70b',
            'llama-3-8b',
            'llama-3.1-8b',
            'llama-3.1-70b',
            'llama-3.1-405b',
            'llama-3.2-1b',
            'llama-3.2-3b',
            'llama-3.2-11b',
            'llama-3.2-90b',
            'llama-3.3-70b'
        },
        "Mistral": {
            'mistral-nemo',
            'mistral-7b',
            'mistral-small-24b',
            'mixtral-8x7b'
        },
        "Microsoft": {
            'phi-4'
        },
        "Google": {
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-2.0-flash',
            'gemini-2.0-pro-exp',
            'gemini-2.5-flash',
            'gemini-2.5-pro'
        },
        "Qwen": {
            'qwen-1.5-7b',
            'qwen-2-72b',
            'qwen-2.5',
            'qwen-2.5-7b',
            'qwen-2.5-72b',
            'qwen-2.5-coder-32b',
            'qwen-3-32b',
            'qwen-3-30b',
            'qwq-32b'
        },
        "DeepSeek": {
            'deepseek-v3',
            'deepseek-r1'
        },
        "xAI": {
            'grok-2',
            'grok-2-mini',
            'early-grok-3',
            'grok-3',
            'grok-3-beta',
            'grok3-mini',
            'grok-3-mini-beta',
            'grok-3-mini-high',
            'grok-3-fast',
            'grok-3-fast-mini',
            'grok-3-r1',
            'grok-3-thinking'
        },
        "Perplexity": {
            'sonar-pro',
            'sonar',
            'sonar-reasoning-pro',
            'sonar-reasoning'
        },
        " Anthropic": {
            'claude-3-7-sonnet',
            'claude-3.5-sonnet',
            'claude-3-sonnet',
            'claude-3-opus',
            'claude-3-haiku'
        }
    }

# Автосохранение кода
def save_code_blocks(response_text, chat_id, lang='en'):
    code_pattern = r'```(\w+)?\n([\s\S]*?)\n```'
    matches = re.findall(code_pattern, response_text)
    
    if not matches:
        return response_text
        
    saved_files = []
    for idx, match in enumerate(matches):
        lang_ext, code = match
        if not lang_ext:
            lang_ext = 'txt'
            
        filename = f"saved_code/{chat_id}_{int(time.time())}_{idx}.{lang_ext}"
        os.makedirs("saved_code", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        saved_files.append(filename)
    
    if saved_files:
        global stats
        stats['saved_code_blocks'] += len(saved_files)
        console.print(f"\n[green]💾 {tr('saved_code_location', lang)}[/]")
        for file in saved_files:
            console.print(f"  → [link=file://{os.path.abspath(file)}]{file}[/]")
        console.print(f"[dim]{tr('code_saved', lang).format(len(saved_files))}[/]")
    
    # Убираем блоки кода из ответа
    return re.sub(code_pattern, '', response_text)

# Подсветка синтаксиса
def highlight_code(text):
    code_pattern = r'```(\w+)?\n([\s\S]*?)\n```'
    
    def replacer(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            lexer = TextLexer()
            
        formatter = TerminalFormatter()
        highlighted = highlight(code, lexer, formatter)
        return highlighted
    
    return re.sub(code_pattern, replacer, text)

# Генерация ответа
def generate_response(user_id: int, chat_id: str, messages: list) -> str:
    user_models = load_user_models()
    model_name = user_models.get(str(user_id), 'gpt-4o')
    
    all_chats = load_user_chats()
    user_chats = all_chats.get(str(user_id), {})
    chat_data = user_chats.get("chats", {}).get(chat_id, {})
    
    saved_provider = chat_data.get("provider")
    providers = init_providers()
    provider_errors = []
    
    # Пробуем сохраненный провайдер
    if saved_provider:
        try:
            provider_class = provider_classes.get(saved_provider)
            if provider_class:
                logger.info(f"Using saved provider: {saved_provider}")
                response = g4f.ChatCompletion.create(
                    model=model_name,
                    messages=messages,
                    provider=provider_class,
                    timeout=60,
                    auto_continue=True
                )
                full_response = ""
                for chunk in response:
                    if isinstance(chunk, str):
                        full_response += chunk
                    if len(full_response) > 10000:
                        break
                
                if full_response.strip():
                    return full_response
        except Exception as e:
            error_msg = f"{saved_provider}: {str(e)[:100]}"
            provider_errors.append(error_msg)
            logger.warning(f"Error in saved provider: {error_msg}")
            chat_data["provider"] = None
            user_chats.setdefault("chats", {})[chat_id] = chat_data
            all_chats[str(user_id)] = user_chats
            save_user_chats(all_chats)

    # Пробуем все доступные провайдеры
    for provider in providers:
        try:
            if saved_provider and provider.__name__ == saved_provider:
                continue
                
            logger.info(f"Trying provider: {provider.__name__}")
            response = g4f.ChatCompletion.create(
                model=model_name,
                messages=messages,
                provider=provider,
                timeout=60,
                auto_continue=True
            )
            full_response = ""
            for chunk in response:
                if isinstance(chunk, str):
                    full_response += chunk
                if len(full_response) > 10000:
                    break
            
            if full_response.strip():
                chat_data["provider"] = provider.__name__
                user_chats.setdefault("chats", {})[chat_id] = chat_data
                all_chats[str(user_id)] = user_chats
                save_user_chats(all_chats)
                return full_response
        except Exception as e:
            error_msg = f"{provider.__name__}: {str(e)[:100]}"
            provider_errors.append(error_msg)
            logger.warning(f"Provider error: {error_msg}")
            time.sleep(0.1)
    
    error_details = "\n".join(provider_errors[-5:])
    return f"⚠️ All providers unavailable. Try later or change model.\n\nErrors:\n{error_details}"

# Обработка размышлений модели
def process_model_thinking(response_text, lang='en'):
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    matches = re.findall(thinking_pattern, response_text, re.DOTALL)
    
    if matches:
        console.print(f"\n[bold yellow]💭 {tr('thinking', lang)}:[/]")
        for i, thought in enumerate(matches, 1):
            thought = thought.strip()
            if thought:
                console.print(f"[dim]{i}.[/] {thought}")
        
        response_text = re.sub(thinking_pattern, '', response_text, flags=re.DOTALL).strip()
    
    return response_text

# Показать справку
def show_help(user_id):
    lang = get_user_lang(user_id)
    
    help_text = (
        f"[bold cyan]🤖 {tr('welcome', lang)} (g4f v0.5.7.5)[/]\n"
        f"[bold]{tr('developer', lang)}:[/] AiTechnologyDev\n"
        f"[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]\n\n"
        f"[bold]{tr('commands', lang)}:[/]\n"
        f"  [bold]/newchat[/]  - {tr('new_chat', lang)}\n"
        f"  [bold]/usechat[/]  - {tr('switch_chat', lang)}\n"
        f"  [bold]/delchat[/]  - {tr('delete_chat', lang)}\n"
        f"  [bold]/chats[/]    - {tr('list_chats', lang)}\n"
        f"  [bold]/setmodel[/] - {tr('set_model', lang)}\n"
        f"  [bold]/mymodel[/]  - {tr('current_model', lang)}\n"
        f"  [bold]/models[/]   - {tr('list_models', lang)}\n"
        f"  [bold]/providers[/]- {tr('list_providers', lang)}\n"
        f"  [bold]/status[/]   - {tr('system_status', lang)}\n"
        f"  [bold]/lang[/]     - {tr('lang', lang)} (en/ru)\n"
        f"  [bold]/stats[/]    - {tr('stats', lang)}\n"
        f"  [bold]/exit[/]     - {tr('exit', lang)}\n"
        f"  [bold]/help[/]     - {tr('help', lang)}\n\n"
        f"[bold cyan]{tr('start_chat', lang)}:[/]"
    )
    
    console.print(Panel(
        help_text,
        title=tr('help_title', lang),
        title_align="left",
        border_style="cyan",
        padding=(1, 2),
        width=80
    ))

# Установка модели
def set_model(user_id, model_name):
    lang = get_user_lang(user_id)
    
    try:
        supported_models = get_supported_models()
        
        if model_name not in supported_models:
            console.print(f"[red]❌ {tr('model_error', lang)}. /models {tr('list_models', lang).lower()}[/]")
            return False
        
        user_models = load_user_models()
        user_models[str(user_id)] = model_name
        save_user_models(user_models)
        
        console.print(f"[green]✅ {tr('model_set', lang)}:[/] [bold]{model_name}[/]")
        return True
    except Exception as e:
        logger.error(f"Model set error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")
        return False

# Создание нового чата
def new_chat(user_id):
    lang = get_user_lang(user_id)
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    chat_id = str(uuid.uuid4())[:8]
    
    chat_list[chat_id] = {
        "history": [{"role": "system", "content": "You are a friendly and helpful AI assistant."}],
        "provider": None
    }
    
    user_chats["chats"] = chat_list
    user_chats["active"] = chat_id
    chats[user_id] = user_chats
    save_user_chats(chats)
    
    global stats
    stats['active_chats'] += 1
    
    console.print(f"[green]🆕 {tr('chat_created', lang)}:[/] [bold]{chat_id}[/]")
    return chat_id

# Переключение чата
def use_chat(user_id, chat_id):
    lang = get_user_lang(user_id)
    
    try:
        user_id = str(user_id)
        chats = load_user_chats()
        user_chats = chats.get(user_id, {})
        chat_list = user_chats.get("chats", {})
        if chat_id in chat_list:
            user_chats["active"] = chat_id
            chats[user_id] = user_chats
            save_user_chats(chats)
            console.print(f"[green]✅ {tr('chat_switched', lang)}:[/] [bold]{chat_id}[/]")
            return True
        else:
            console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
            return False
    except Exception:
        console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
        return False

# Удаление чата
def del_chat(user_id, chat_id):
    lang = get_user_lang(user_id)
    
    try:
        user_id = str(user_id)
        chats = load_user_chats()
        user_chats = chats.get(user_id, {})
        chat_list = user_chats.get("chats", {})
        if chat_id in chat_list:
            del chat_list[chat_id]
            if user_chats.get("active") == chat_id:
                new_active = next(iter(chat_list.keys()), None) if chat_list else None
                if new_active:
                    user_chats["active"] = new_active
                else:
                    new_chat_id = str(uuid.uuid4())[:8]
                    chat_list[new_chat_id] = {
                        "history": [{"role": "system", "content": "You are a friendly and helpful AI assistant."}],
                        "provider": None
                    }
                    user_chats["active"] = new_chat_id
            user_chats["chats"] = chat_list
            chats[user_id] = user_chats
            save_user_chats(chats)
            
            global stats
            stats['active_chats'] = max(0, stats['active_chats'] - 1)
            
            console.print(f"[yellow]🗑️ {tr('chat_deleted', lang)}: [bold]{chat_id}[/][/]")
            return True
        else:
            console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
            return False
    except Exception:
        console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
        return False

# Список чатов
def list_chats(user_id):
    lang = get_user_lang(user_id)
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    active_id = user_chats.get("active", "default")
    
    if not chat_list:
        console.print(f"[yellow]{tr('no_chats', lang)}[/]")
        return
    
    panel_text = ""
    for cid in chat_list:
        mark = "🟢" if cid == active_id else "⚪"
        panel_text += f"[bold]{mark} {cid}[/]\n"
    
    console.print(Panel(
        panel_text.strip(),
        title=f"[bold cyan]{tr('your_chats', lang)}[/]",
        title_align="left",
        border_style="blue",
        padding=(0, 2),
        width=60
    ))

# Показать текущую модель
def show_model(user_id):
    lang = get_user_lang(user_id)
    
    try:
        user_models = load_user_models()
        model = user_models.get(str(user_id), 'gpt-4o (default)')
        console.print(Panel(
            f"[bold]{model}[/]",
            title=f"[cyan]{tr('current_model_title', lang)}[/]",
            title_align="left",
            border_style="green",
            padding=(0, 2),
            width=60
        ))
    except Exception as e:
        logger.error(f"Model show error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

# Список моделей
def list_models(user_id):
    lang = get_user_lang(user_id)
    
    try:
        models_dict = get_supported_models()
        panel_text = ""
        
        for provider, models in models_dict.items():
            panel_text += f"\n[bold underline]{provider}:[/]\n"
            for model in sorted(models):
                panel_text += f"  - {model}\n"
        
        console.print(Panel(
            panel_text.strip(),
            title=f"[cyan]{tr('available_models', lang)} (g4f 0.5.7.5)[/]",
            title_align="left",
            border_style="magenta",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Model list error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

# Список провайдеров
def list_providers(user_id):
    lang = get_user_lang(user_id)
    
    try:
        providers = init_providers()
        panel_text = "\n".join([f"- [bold]{provider.__name__}[/]" for provider in providers])
        
        console.print(Panel(
            f"{panel_text}\n\n[bold yellow]{tr('total_providers', lang)}: {len(providers)}[/]",
            title=f"[cyan]{tr('providers_title', lang)}[/]",
            title_align="left",
            border_style="yellow",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Provider list error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

# Статус системы
def system_status(user_id):
    lang = get_user_lang(user_id)
    
    try:
        # Get all supported models
        models_dict = get_supported_models()
        total_models = sum(len(models) for models in models_dict.values())
        
        # Get active providers count
        providers = init_providers()
        
        # Get current model
        user_models = load_user_models()
        current_model = user_models.get(str(user_id), 'gpt-4o (default)')
        
        # Format last activity time
        last_activity = time.strftime(tr('time_format', lang), time.localtime(stats['last_activity']))
        
        console.print(Panel(
            f"[bold]{tr('current_model_title', lang)}:[/] {current_model}\n"
            f"[bold]{tr('available_models', lang)}:[/] {total_models}\n"
            f"[bold]{tr('active_providers', lang)}:[/] {len(providers)}\n"
            f"[bold]{tr('active_chats', lang)}:[/] {stats['active_chats']}\n"
            f"[bold]{tr('total_messages', lang)}:[/] {stats['total_messages']}\n"
            f"[bold]{tr('saved_blocks', lang)}:[/] {stats['saved_code_blocks']}\n"
            f"[bold]{tr('last_activity', lang)}:[/] {last_activity}\n"
            f"[bold]System:[/] {sys.platform}\n"
            f"[bold]Python:[/] {sys.version.split()[0]}",
            title=f"[cyan]{tr('system_status_title', lang)}[/]",
            title_align="left",
            border_style="green",
            padding=(1, 2),
            width=70
        ))
    except Exception as e:
        logger.error(f"Status error: {e}")
        console.print(f"[red]❌ {tr('gen_error', lang)}[/]")

# Показать статистику
def show_stats(user_id):
    lang = get_user_lang(user_id)
    
    try:
        console.print(Panel(
            f"[bold]{tr('total_messages', lang)}:[/] {stats['total_messages']}\n"
            f"[bold]{tr('saved_blocks', lang)}:[/] {stats['saved_code_blocks']}\n"
            f"[bold]{tr('active_chats', lang)}:[/] {stats['active_chats']}\n"
            f"[bold]{tr('last_activity', lang)}:[/] {time.strftime(tr('time_format', lang), time.localtime(stats['last_activity']))}",
            title=f"[cyan]{tr('stats_title', lang)}[/]",
            title_align="left",
            border_style="blue",
            padding=(1, 2),
            width=60
        ))
    except Exception as e:
        logger.error(f"Stats error: {e}")
        console.print(f"[red]❌ {tr('gen_error', lang)}[/]")

# Основная функция чата
def chat_loop():
    user_id = 1  # Для консольной версии используем одного пользователя
    lang = get_user_lang(user_id)
    
    # Создаем папки при запуске
    os.makedirs("saved_code", exist_ok=True)
    
    chats = load_user_chats()
    user_chats = chats.get(str(user_id), {})
    active_id = user_chats.get("active", None)
    
    # Создаем чат если нет активного
    if not active_id or active_id not in user_chats.get("chats", {}):
        active_id = new_chat(user_id)
    
    # Приветственное сообщение
    console.print(Panel(
        f"[bold cyan]{tr('welcome', lang)}[/] (g4f v0.5.7.5)\n"
        f"[bold]{tr('developer', lang)}:[/] AiTechnologyDev\n"
        f"[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]",
        title=f"[cyan]{tr('welcome_menu', lang)}[/]",
        title_align="center",
        border_style="bright_cyan",
        padding=(1, 4),
        width=80
    ))
    
    show_help(user_id)
    init_providers()
    
    while True:
        try:
            console.print(f"\n[bold cyan]{tr('chat_prompt', lang)}:[/] ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
                
            # Обновляем статистику
            stats['total_messages'] += 1
            stats['last_activity'] = time.time()
                
            # Обработка команд
            if user_input.startswith('/'):
                cmd = user_input.split()[0].lower()
                
                if cmd == '/exit':
                    console.print(f"[bold yellow]{tr('exit_confirmation', lang)}[/]")
                    break
                    
                elif cmd == '/help':
                    show_help(user_id)
                    
                elif cmd == '/newchat':
                    active_id = new_chat(user_id)
                    
                elif cmd == '/usechat':
                    if len(user_input.split()) > 1:
                        chat_id = user_input.split()[1].strip()
                        if use_chat(user_id, chat_id):
                            active_id = chat_id
                    else:
                        console.print(f"[red]❌ {tr('chat_not_found', lang)}: /usechat <id>[/]")
                        
                elif cmd == '/delchat':
                    if len(user_input.split()) > 1:
                        chat_id = user_input.split()[1].strip()
                        del_chat(user_id, chat_id)
                    else:
                        console.print(f"[red]❌ {tr('chat_not_found', lang)}: /delchat <id>[/]")
                        
                elif cmd == '/chats':
                    list_chats(user_id)
                    
                elif cmd == '/setmodel':
                    if len(user_input.split()) > 1:
                        model_name = user_input.split(maxsplit=1)[1].strip()
                        set_model(user_id, model_name)
                    else:
                        console.print(f"[red]❌ {tr('model_error', lang)}: /setmodel <name>[/]")
                        
                elif cmd == '/mymodel':
                    show_model(user_id)
                    
                elif cmd == '/models':
                    list_models(user_id)
                    
                elif cmd == '/providers':
                    list_providers(user_id)
                    
                elif cmd == '/status':
                    system_status(user_id)
                    
                elif cmd == '/lang':
                    if len(user_input.split()) > 1:
                        new_lang = user_input.split()[1].strip().lower()
                        if new_lang in ['en', 'ru']:
                            save_user_lang(user_id, new_lang)
                            lang = new_lang
                            console.print(f"[green]✅ {tr('lang_set', lang)}: {new_lang}[/]")
                        else:
                            console.print(f"[red]❌ {tr('invalid_lang', lang)}[/]")
                    else:
                        console.print(f"[yellow]Current language: {lang}[/]")
                
                elif cmd == '/stats':
                    show_stats(user_id)
                    
                else:
                    console.print(f"[red]❌ {tr('unknown_command', lang)}. /help {tr('help', lang).lower()}[/]")
                    
                continue
            
            # Получение истории чата
            all_chats = load_user_chats()
            user_chats = all_chats.get(str(user_id), {})
            chat_data = user_chats.get("chats", {}).get(active_id, {})
            history = chat_data.get("history", [])
            
            # Добавление сообщения пользователя
            user_message = {"role": "user", "content": user_input}
            history.append(user_message)
            
            # Обновление истории
            chat_data["history"] = history
            user_chats.setdefault("chats", {})[active_id] = chat_data
            all_chats[str(user_id)] = user_chats
            save_user_chats(all_chats)
            
            # Генерация ответа с прогресс-баром
            response_text = ""
            with Progress(
                SpinnerColumn(),
                TextColumn(f"[bold blue]{tr('generating', lang)}"),
                transient=True,
                console=console
            ) as progress:
                task = progress.add_task(tr('generating', lang), total=None)
                
                try:
                    response_text = generate_response(user_id, active_id, history)
                    
                    # Добавление ответа в историю
                    if response_text and not response_text.startswith("⚠️"):
                        assistant_message = {"role": "assistant", "content": response_text}
                        history.append(assistant_message)
                        chat_data["history"] = history
                        user_chats.setdefault("chats", {})[active_id] = chat_data
                        all_chats[str(user_id)] = user_chats
                        save_user_chats(all_chats)
                    
                    # Обработка размышлений
                    response_text = process_model_thinking(response_text, lang)
                    
                    # Автосохранение кода
                    response_text = save_code_blocks(response_text, active_id, lang)
                    
                    # Вывод ответа
                    console.print(f"\n[bold cyan]🤖 {tr('ai_prompt', lang)}:[/]")
                    try:
                        # Подсветка синтаксиса
                        highlighted = highlight_code(response_text)
                        console.print(highlighted)
                    except:
                        # Простой вывод в случае ошибки
                        console.print(response_text)
                    
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    console.print(f"\n[red]⚠️ {tr('gen_error', lang)}[/]")
                
                progress.update(task, completed=100)
                
        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]{tr('exit', lang)}: /exit[/]")
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            console.print(f"[red]⚠️ {tr('main_error', lang)}[/]")

if __name__ == '__main__':
    chat_loop()