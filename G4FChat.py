# G4FChat.py

import uuid
import g4f
import json
import logging
import sys
import time
import inspect
import os
import re
import textwrap
from threading import Lock
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.style import Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import TerminalFormatter
from typing import Dict, List, Set, Tuple, Optional, Any, Union

# Import new AsyncClient if available
try:
    from g4f.client import Client as G4FClient
    USE_CLIENT_API = True
except ImportError:
    USE_CLIENT_API = False
    logging.info("G4F Client API not found, falling back to legacy API.")

try:
    from g4f.version import __version__ as G4F_VERSION
except ImportError:
    G4F_VERSION = '0.5.7.5'

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_chat.log',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()
error_style = Style(color="red", bold=True)
success_style = Style(color="green", bold=True)
ai_style = Style(color="cyan", bold=True)
code_style = Style(color="magenta")

# Configuration files
MODEL_FILE = 'user_models.json'
USER_CHATS_FILE = 'user_chats.json'
LANG_FILE = 'user_lang.json'
CONFIG_DIR = 'chat_config'

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

# Caching
user_models_cache: Dict[str, str] = {}
user_chats_cache: Dict[str, dict] = {}
user_lang_cache: Dict[str, str] = {}
active_providers: List[g4f.Provider.BaseProvider] = []
provider_classes: Dict[str, g4f.Provider.BaseProvider] = {}

# Global stats
stats = {
    'total_messages': 0,
    'saved_code_blocks': 0,
    'active_chats': 0,
    'last_activity': time.time(),
    'total_api_calls': 0
}

# Thread safety
cache_lock = Lock()

# Provider management
# Updated based on common provider names and potential instability
BLACKLISTED_PROVIDERS = {
    'BlackForestLabs_Flux1Dev', 'DeepInfra', 'FlowGpt', 'Free2GPT',
    'ImageLabs', 'HuggingFace', 'PollinationsImage', 'StabilityAI_SD35Large', 'Bing'
}
BACKUP_PROVIDERS = {'You', 'Liaobots', 'PerplexityLabs'} # Updated list

# Enhanced translation system
TRANSLATIONS = {
    'en': {
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
        'start_chat': "Type a message or question",
        'ai_prompt': "AI",
        'thinking': "Model reflections",
        'saving_code': "Saved code blocks",
        'generating': "Generating response...",
        'model_set': "Model set",
        'model_error': "Model not available",
        'chat_created': "New chat created",
        'chat_switched': "Switched to chat",
        'chat_not_found': "Chat not found",
        'chat_deleted': "Chat deleted",
        'no_chats': "No chats available",
        'your_chats': "Your Chats",
        'available_models': "Available models",
        'active_providers': "Active providers",
        'system_status_title': "System status",
        'exit_confirmation': "Exiting...",
        'unknown_command': "Unknown command",
        'gen_error': "Response error",
        'main_error': "Error occurred",
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
        'saved_code_location': "Code saved to:",
        'api_calls': "API calls",
        'model_optimization': "Model optimization",
        'chat_history': "Chat history",
        'token_count': "Token count",
        'timeout_error': "Request timed out. Trying another provider...",
        'no_response_error': "Received empty response. Trying another provider...",
        'using_client_api': "Using G4F Client API",
        'using_legacy_api': "Using G4F Legacy API"
    },
    'ru': {
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
        'start_chat': "Введите сообщение или вопрос",
        'ai_prompt': "ИИ",
        'thinking': "Размышления модели",
        'saving_code': "Сохраненные блоки кода",
        'generating': "Генерация ответа...",
        'model_set': "Модель установлена",
        'model_error': "Модель недоступна",
        'chat_created': "Новый чат создан",
        'chat_switched': "Переключено на чат",
        'chat_not_found': "Чат не найден",
        'chat_deleted': "Чат удален",
        'no_chats': "Чаты отсутствуют",
        'your_chats': "Ваши чаты",
        'available_models': "Доступные модели",
        'active_providers': "Активные провайдеры",
        'system_status_title': "Статус системы",
        'exit_confirmation': "Выход...",
        'unknown_command': "Неизвестная команда",
        'gen_error': "Ошибка генерации",
        'main_error': "Ошибка выполнения",
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
        'saved_code_location': "Код сохранён в:",
        'api_calls': "API вызовы",
        'model_optimization': "Оптимизация модели",
        'chat_history': "История чата",
        'token_count': "Токены",
        'timeout_error': "Время запроса истекло. Пробуем другого провайдера...",
        'no_response_error': "Получен пустой ответ. Пробуем другого провайдера...",
        'using_client_api': "Используется G4F Client API",
        'using_legacy_api': "Используется G4F Legacy API"
    }
}

def tr(key: str, lang: str = 'en') -> str:
    """Get translation for key with fallback"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def get_user_lang(user_id: str) -> str:
    """Get user language with caching"""
    user_id = str(user_id)
    if not user_lang_cache:
        load_lang_cache()
    return user_lang_cache.get(user_id, 'en')

def save_user_lang(user_id: str, lang: str) -> None:
    """Save user language"""
    user_id = str(user_id)
    with cache_lock:
        user_lang_cache[user_id] = lang
        save_lang_cache()

def load_lang_cache() -> None:
    """Load language cache from file"""
    global user_lang_cache
    try:
        lang_file = os.path.join(CONFIG_DIR, LANG_FILE)
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as f:
                user_lang_cache = json.load(f)
        else:
            user_lang_cache = {}
    except Exception as e:
        logger.error(f"Language load error: {e}")
        user_lang_cache = {}

def save_lang_cache() -> None:
    """Save language cache to file"""
    try:
        lang_file = os.path.join(CONFIG_DIR, LANG_FILE)
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(user_lang_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving language: {e}")

def get_all_providers() -> List[g4f.Provider.BaseProvider]:
    """Get all available providers"""
    providers = []
    for _, obj in inspect.getmembers(g4f.Provider):
        if inspect.isclass(obj) and issubclass(obj, g4f.Provider.BaseProvider) and obj != g4f.Provider.BaseProvider:
            providers.append(obj)
    return providers

def init_providers() -> List[g4f.Provider.BaseProvider]:
    """Initialize and cache providers"""
    global active_providers, provider_classes
    with cache_lock:
        if active_providers:
            return active_providers
        logger.info("Initializing providers...")
        all_providers = get_all_providers()
        active_providers = []
        provider_classes = {}
        # Prioritize backup providers
        for provider in all_providers:
            provider_name = provider.__name__
            if provider_name in BACKUP_PROVIDERS and provider_name not in BLACKLISTED_PROVIDERS:
                try:
                    # Use hasattr for safer check if 'working' attribute might not exist
                    if getattr(provider, 'working', True):
                        active_providers.append(provider)
                        provider_classes[provider_name] = provider
                        logger.info(f"Added backup provider: {provider_name}")
                except Exception as e:
                    logger.warning(f"Backup provider error {provider_name}: {str(e)[:100]}")
        # Add other working providers
        for provider in all_providers:
            provider_name = provider.__name__
            if (provider_name not in BLACKLISTED_PROVIDERS and
                provider_name not in BACKUP_PROVIDERS and
                provider not in active_providers):
                try:
                    if getattr(provider, 'working', True):
                        active_providers.append(provider)
                        provider_classes[provider_name] = provider
                        logger.info(f"Added provider: {provider_name}")
                except Exception as e:
                    logger.warning(f"Provider error {provider_name}: {str(e)[:100]}")
        if not active_providers:
            logger.error("No providers available! Using fallback")
            # Consider adding a more robust fallback or raising an error
        logger.info(f"Active providers: {len(active_providers)}")
        return active_providers

def load_user_models() -> Dict[str, str]:
    """Load user models with caching"""
    global user_models_cache
    with cache_lock:
        if user_models_cache:
            return user_models_cache
        try:
            model_file = os.path.join(CONFIG_DIR, MODEL_FILE)
            if os.path.exists(model_file):
                with open(model_file, 'r', encoding='utf-8') as f:
                    user_models_cache = json.load(f)
            else:
                user_models_cache = {}
        except Exception as e:
            logger.error(f"Model load error: {e}")
            user_models_cache = {}
        return user_models_cache

def save_user_models(data: Dict[str, str]) -> None:
    """Save user models"""
    global user_models_cache
    with cache_lock:
        user_models_cache = data
        try:
            model_file = os.path.join(CONFIG_DIR, MODEL_FILE)
            with open(model_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving models: {e}")

def load_user_chats() -> Dict[str, dict]:
    """Load user chats with caching"""
    global user_chats_cache, stats
    with cache_lock:
        if user_chats_cache:
            return user_chats_cache
        try:
            chat_file = os.path.join(CONFIG_DIR, USER_CHATS_FILE)
            if os.path.exists(chat_file):
                with open(chat_file, 'r', encoding='utf-8') as f:
                    user_chats_cache = json.load(f)
                # Update stats
                stats['active_chats'] = 0
                for user_data in user_chats_cache.values():
                    chats = user_data.get("chats", {})
                    stats['active_chats'] += len(chats)
                    for chat_data in chats.values():
                        stats['total_messages'] += len(chat_data.get("history", []))
            else:
                user_chats_cache = {}
        except Exception as e:
            logger.error(f"Chat load error: {e}")
            user_chats_cache = {}
        return user_chats_cache

def save_user_chats(data: Dict[str, dict]) -> None:
    """Save user chats"""
    global user_chats_cache, stats
    with cache_lock:
        user_chats_cache = data
        # Update stats
        stats['active_chats'] = 0
        stats['total_messages'] = 0
        for user_data in data.values():
            chats = user_data.get("chats", {})
            stats['active_chats'] += len(chats)
            for chat_data in chats.values():
                stats['total_messages'] += len(chat_data.get("history", []))
        stats['last_activity'] = time.time()
        try:
            chat_file = os.path.join(CONFIG_DIR, USER_CHATS_FILE)
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving chats: {e}")

def get_supported_models():
    """Define supported models by provider. Keeping original structure, adding new models."""
    models = {
        # [Previous model definitions remain the same...]
        "Thinking Models": {
            'o1',
            'o1-mini',
            'o1-pro',
            'o4-mini',
            'o4-mini-high',
            'o3',
            'o3-mini',
            'o3-mini-high',
            'qwq-32b',
            'deepseek-r1',
            'grok-3-r1',
            'grok-3-thinking',
            'sonar-reasoning-pro',
            'sonar-reasoning',
            'claude-3.5-sonnet',
            'llama-3.3-70b',
            'qwen-2.5-coder-32b'
        }
    }
    # Merge with existing models - ADDED NEW MODELS HERE
    full_models = {
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
            'gpt-4o-2024-08-06', # Added newer specific version
            'gpt-4o-realtime-preview-2024-10-01', # Added new model
            'gpt-4o-realtime-preview', # Added new model alias
            'gpt-4o-audio-preview', # Added new model
            'gpt-4o-audio-preview-2024-10-01', # Added new model
            'o1-preview', # Added new model
            'o1-mini' # Added new model
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
            'llama-3.3-70b-instruct', # Added new model
            'Meta-Llama-3.1-8B-Instruct', # Added alternative naming
            'Meta-Llama-3.1-70B-Instruct', # Added alternative naming
            'Llama-3.2-11B-Vision-Instruct', # Added vision model
            'Llama-3.2-90B-Vision-Instruct' # Added vision model
        },
        "Mistral": {
            'mistral-nemo',
            'mistral-7b',
            'mistral-small-24b',
            'mixtral-8x7b',
            'mistral-tiny',
            'mistral-small',
            'mistral-medium',
            'mistral-large',
            'open-mistral-nemo',
            'open-codestral-mamba',
            'pixtral-12b-2409', # Added new model
            'ministral-3b-2410', # Added new model
            'ministral-8b-2410', # Added new model
            'mistral-small-24b-2410', # Added new model
            'mistral-large-2411' # Added new model
        },
        "Microsoft": {
            'phi-4',
            'phi-3-medium-128k-instruct',
            'phi-3-mini-128k-instruct',
            'Phi-3-medium-128k-instruct', # Added alternative naming
            'Phi-3-mini-128k-instruct' # Added alternative naming
        },
        "Google": {
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-2.0-flash',
            'gemini-2.0-pro-exp',
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-1.5-flash-002', # Added newer specific version
            'gemini-1.5-pro-002', # Added newer specific version
            'gemini-2.0-flash-exp', # Added new experimental model
            'gemini-2.0-pro-exp' # Added new experimental model
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
            'qwen-2.5-7b-instruct', # Added new model
            'qwen-2.5-72b-instruct', # Added new model
            'qwen-3-72b-instruct', # Added new model
            'qwen-2.5-coder-32b-instruct', # Added new model
            'qwq' # Added new model
        },
        "DeepSeek": {
            'deepseek-v3',
            'deepseek-chat',
            'deepseek-coder',
            'deepseek-r1' # Added new model
        },
        "xAI": {
            'grok-2',
            'grok-2-mini',
            'early-grok-3',
            'grok-3',
            'grok-3-beta',
            'grok-3-mini',
            'grok-3-mini-beta',
            'grok-3-mini-high',
            'grok-3-fast',
            'grok-3-fast-mini',
            'grok-2-vision-beta' # Added new model
        },
        "Perplexity": {
            'sonar-pro',
            'sonar',
            'sonar-reasoning-pro', # Added new model
            'sonar-reasoning', # Added new model
            'llama-3.1-sonar-small-128k-online', # Added new model
            'llama-3.1-sonar-large-128k-online', # Added new model
            'llama-3.1-sonar-huge-128k-online' # Added new model
       },
        "Anthropic": {
            'claude-3-7-sonnet',
            'claude-3.5-sonnet',
            'claude-3-sonnet',
            'claude-3-opus',
            'claude-3-haiku',
            'claude-3-5-sonnet-20240620', # Added specific version
            'claude-3-5-sonnet-20241022', # Added newer specific version
            'claude-3.7-sonnet' # Added new model
        },
        "Reasoning Specialists": models["Thinking Models"]
    }
    return full_models

def save_code_blocks(response_text: str, chat_id: str, lang: str = 'en') -> str:
    """Save code blocks from response and return cleaned text"""
    # Corrected regex pattern using raw string concatenation
    code_pattern = r'```(\w+)?\n([\s\S]*?)\n```'
    matches = re.findall(code_pattern, response_text)
    if not matches:
        return response_text
    saved_files = []
    code_dir = os.path.join(CONFIG_DIR, "saved_code")
    os.makedirs(code_dir, exist_ok=True)
    for idx, (lang_ext, code) in enumerate(matches):
        if not lang_ext:
            lang_ext = 'txt'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"code_{chat_id}_{timestamp}_{idx}.{lang_ext}"
        filepath = os.path.join(code_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
            saved_files.append(filepath)
        except Exception as e:
            logger.error(f"Code save error: {e}")
    if saved_files:
        stats['saved_code_blocks'] += len(saved_files)
        console.print(f"\n[green]💾 {tr('saved_code_location', lang)}[/]")
        for file in saved_files:
            console.print(f"  → [link=file://{os.path.abspath(file)}]{os.path.basename(file)}[/]")
        console.print(f"[dim]{tr('code_saved', lang).format(len(saved_files))}[/]")
    # Remove code blocks from response
    return re.sub(code_pattern, '', response_text)

def highlight_code(text: str) -> str:
    """Syntax highlighting for code blocks"""
    # Corrected regex pattern using raw string concatenation
    code_pattern = r'```(\w+)?\n([\s\S]*?)\n```'
    def replacer(match):
        lang = match.group(1) or 'text'
        code = match.group(2)
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            lexer = TextLexer()
        formatter = TerminalFormatter()
        return highlight(code, lexer, formatter)
    return re.sub(code_pattern, replacer, text)

def generate_response(user_id: str, chat_id: str, messages: list) -> str:
    """Enhanced response generator with provider fallback"""
    user_models = load_user_models()
    model_name = user_models.get(user_id, 'gpt-4o')
    lang = get_user_lang(user_id)
    all_chats = load_user_chats()
    user_chats = all_chats.get(user_id, {})
    chat_data = user_chats.get("chats", {}).get(chat_id, {})
    saved_provider = chat_data.get("provider")
    providers = init_providers()
    provider_errors = []
    timeout_duration = 60 # seconds

    # Try saved provider first
    if saved_provider and saved_provider in provider_classes:
        try:
            provider = provider_classes[saved_provider]
            logger.info(f"Trying saved provider: {saved_provider}")
            if USE_CLIENT_API:
                # Use new Client API if available
                client = G4FClient(provider=provider)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    timeout=timeout_duration
                )
                full_response = response.choices[0].message.content
            else:
                # Fallback to legacy API
                response = g4f.ChatCompletion.create(
                    model=model_name,
                    messages=messages,
                    provider=provider,
                    timeout=timeout_duration
                )
                full_response = "".join(response)

            if full_response and full_response.strip():
                stats['total_api_calls'] += 1
                return full_response[:15000]  # Limit response size
            else:
                raise ValueError(tr('no_response_error', lang))
        except TimeoutError:
            error_msg = f"{saved_provider}: {tr('timeout_error', lang)}"
            provider_errors.append(error_msg)
            logger.warning(f"Saved provider timeout: {error_msg}")
        except Exception as e:
            error_msg = f"{saved_provider}: {str(e)[:100]}"
            provider_errors.append(error_msg)
            logger.warning(f"Saved provider error: {error_msg}")

    # Try all available providers
    for provider in providers:
        provider_name = provider.__name__
        if provider_name == saved_provider:
            continue
        try:
            logger.info(f"Trying provider: {provider_name}")
            if USE_CLIENT_API:
                client = G4FClient(provider=provider)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    timeout=timeout_duration
                )
                full_response = response.choices[0].message.content
            else:
                response = g4f.ChatCompletion.create(
                    model=model_name,
                    messages=messages,
                    provider=provider,
                    timeout=timeout_duration
                )
                full_response = "".join(response)

            if full_response and full_response.strip():
                # Save successful provider
                chat_data["provider"] = provider_name
                user_chats.setdefault("chats", {})[chat_id] = chat_data
                all_chats[user_id] = user_chats
                save_user_chats(all_chats)
                stats['total_api_calls'] += 1
                return full_response
            else:
                raise ValueError(tr('no_response_error', lang))
        except TimeoutError:
            error_msg = f"{provider_name}: {tr('timeout_error', lang)}"
            provider_errors.append(error_msg)
            logger.warning(f"Provider timeout: {error_msg}")
        except Exception as e:
            error_msg = f"{provider_name}: {str(e)[:100]}"
            provider_errors.append(error_msg)
            logger.warning(f"Provider error: {error_msg}")
            time.sleep(0.3)  # Brief delay between attempts

    # Error handling
    error_details = [
        f"[red]❌ {tr('gen_error', lang)}[/]",
        f"[yellow]Tried {len(providers)} providers[/]",
        f"[dim]Model: {model_name}[/]"
    ]
    if provider_errors:
        error_details.append("\n[bold]Recent errors:[/]")
        for error in provider_errors[-3:]:
            error_details.append(f"  - {error}")
    error_details.append("\n[blue]Suggestions:")
    error_details.append("  1. Try again later")
    error_details.append("  2. Change model (/setmodel)")
    error_details.append("  3. Check /status for system info[/]")
    return "\n".join(error_details)

def process_model_thinking(response_text: str, lang: str = 'en') -> str:
    """Process and visualize model thinking patterns"""
    thinking_patterns = [
        (r'<thinking>(.*?)</thinking>', 1, "dim"),
        (r'\[reasoning\](.*?)\[/reasoning\]', 2, "cyan"),
        (r'<analysis>(.*?)</analysis>', 3, "bright_white")
    ]
    console.print(f"\n[bold yellow]🧠 {tr('thinking', lang)}[/]")
    for pattern, depth, style in thinking_patterns:
        matches = re.findall(pattern, response_text, re.DOTALL)
        for thought in matches:
            if isinstance(thought, tuple):
                thought = thought[0]
            thought = thought.strip()
            if depth == 1:
                console.print(f"[{style}]└─○ {thought}[/]")
            elif depth == 2:
                console.print(f"[{style}]   └─▶ {thought}[/]")
            elif depth == 3:
                console.print(f"[{style}]      └─★ {thought}[/]")
            response_text = re.sub(pattern, '', response_text, flags=re.DOTALL)
    return response_text.strip()

def show_help(user_id: str) -> None:
    """Show help menu"""
    lang = get_user_lang(user_id)
    g4f_version = getattr(g4f, 'version', 'unknown')
    api_type = tr('using_client_api', lang) if USE_CLIENT_API else tr('using_legacy_api', lang)
    help_text = (
        f"[bold cyan]🤖 {tr('welcome', lang)} (g4f v{g4f_version})[/]\n"
        f"[dim]{api_type}[/]\n"
        f"[bold]{tr('developer', lang)}:[/] AiTechnologyDev\n"
        f"[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]\n"
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
        f"  [bold]/help[/]     - {tr('help', lang)}\n"
        f"[bold cyan]{tr('start_chat', lang)}[/]"
    )
    console.print(Panel(
        help_text,
        title=tr('help_title', lang),
        border_style="cyan",
        padding=(1, 2),
        width=80
    ))

def set_model(user_id: str, model_name: str) -> bool:
    """Set user model"""
    lang = get_user_lang(user_id)
    try:
        supported_models = get_supported_models()
        all_models = set().union(*supported_models.values())
        if model_name not in all_models:
            similar = [m for m in all_models if model_name.lower() in m.lower()]
            console.print(f"[red]❌ {tr('model_error', lang)}: '{model_name}'[/]")
            if similar:
                console.print(f"[yellow]Similar models:[/]")
                for model in similar[:5]: # Limit suggestions
                    console.print(f"  - {model}")
            return False
        user_models = load_user_models()
        user_models[user_id] = model_name
        save_user_models(user_models)
        console.print(f"[green]✅ {tr('model_set', lang)}: [bold]{model_name}[/][/]")
        return True
    except Exception as e:
        logger.error(f"Model set error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")
        return False

def new_chat(user_id: str) -> str:
    """Create new chat"""
    lang = get_user_lang(user_id)
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    chat_id = str(uuid.uuid4())[:8]
    # Get current model
    user_models = load_user_models()
    current_model = user_models.get(user_id, 'gpt-4o')
    # System message based on model
    specialized_models = get_supported_models().get("Reasoning Specialists", set())
    if current_model in specialized_models:
        system_msg = (
            "You are an advanced AI specialist. Your responses should include:\n"
            "1. Detailed analysis (<thinking>analysis</thinking>)\n"
            "2. Step-by-step reasoning\n"
            "3. Confidence estimates\n"
            "Format reasoning between <thinking> tags"
        )
    else:
        system_msg = "You are a helpful AI assistant. Provide clear, concise responses."
    chat_list[chat_id] = {
        "history": [{"role": "system", "content": system_msg}],
        "provider": None,
        "created": time.time()
    }
    user_chats["chats"] = chat_list
    user_chats["active"] = chat_id
    chats[user_id] = user_chats
    save_user_chats(chats)
    stats['active_chats'] += 1
    console.print(f"[green]🆕 {tr('chat_created', lang)}: [bold]{chat_id}[/][/]")
    return chat_id

def use_chat(user_id: str, chat_id: str) -> bool:
    """Switch to chat"""
    lang = get_user_lang(user_id)
    try:
        user_id = str(user_id)
        chats = load_user_chats()
        user_chats = chats.get(user_id, {})
        if chat_id in user_chats.get("chats", {}):
            user_chats["active"] = chat_id
            chats[user_id] = user_chats
            save_user_chats(chats)
            console.print(f"[green]✅ {tr('chat_switched', lang)}: [bold]{chat_id}[/][/]")
            return True
        else:
            console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
            return False
    except Exception:
        console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
        return False

def del_chat(user_id: str, chat_id: str) -> bool:
    """Delete chat"""
    lang = get_user_lang(user_id)
    try:
        user_id = str(user_id)
        chats = load_user_chats()
        user_chats = chats.get(user_id, {})
        chat_list = user_chats.get("chats", {})
        if chat_id in chat_list:
            del chat_list[chat_id]
            if user_chats.get("active") == chat_id:
                user_chats["active"] = next(iter(chat_list.keys()), None) if chat_list else None
            user_chats["chats"] = chat_list
            chats[user_id] = user_chats
            save_user_chats(chats)
            stats['active_chats'] = max(0, stats['active_chats'] - 1)
            console.print(f"[yellow]🗑️ {tr('chat_deleted', lang)}: [bold]{chat_id}[/][/]")
            return True
        else:
            console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
            return False
    except Exception:
        console.print(f"[red]❌ {tr('chat_not_found', lang)}[/]")
        return False

def list_chats(user_id: str) -> None:
    """List user chats"""
    lang = get_user_lang(user_id)
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    active_id = user_chats.get("active")
    if not chat_list:
        console.print(f"[yellow]{tr('no_chats', lang)}[/]")
        return
    panel_text = ""
    for cid, data in chat_list.items():
        mark = "🟢" if cid == active_id else "⚪"
        msg_count = len(data.get("history", [])) - 1  # Exclude system message
        panel_text += f"[bold]{mark} {cid}[/] - {msg_count} msgs\n"
    console.print(Panel(
        panel_text.strip(),
        title=f"[bold cyan]{tr('your_chats', lang)}[/]",
        border_style="blue",
        padding=(0, 2),
        width=60
    ))

def show_model(user_id: str) -> None:
    """Show current model"""
    lang = get_user_lang(user_id)
    try:
        user_models = load_user_models()
        model = user_models.get(str(user_id), 'gpt-4o')
        console.print(Panel(
            f"[bold]{model}[/]",
            title=f"[cyan]{tr('current_model', lang)}[/]",
            border_style="green",
            padding=(0, 2),
            width=60
        ))
    except Exception as e:
        logger.error(f"Model show error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

def list_models(user_id: str) -> None:
    """List available models"""
    lang = get_user_lang(user_id)
    g4f_version = getattr(g4f, 'version', 'unknown')
    try:
        models_dict = get_supported_models()
        panel_text = ""
        for provider, models in models_dict.items():
            panel_text += f"\n[bold underline]{provider}:[/]\n"
            for model in sorted(models):
                if provider == "Reasoning Specialists": # Updated category name
                    panel_text += f"  - [bright_cyan]{model} ⚙️[/]\n"
                else:
                    panel_text += f"  - {model}\n"
        console.print(Panel(
            panel_text.strip(),
            title=f"[cyan]{tr('available_models', lang)} (g4f v{G4F_VERSION})[/]",
            subtitle="⚙️ = Specialized Model",
            border_style="magenta",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Model list error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

def list_providers(user_id: str) -> None:
    """List active providers"""
    lang = get_user_lang(user_id)
    try:
        providers = init_providers()
        panel_text = "\n".join([f"- [bold]{provider.__name__}[/]" for provider in providers])
        console.print(Panel(
            f"{panel_text}\n[bold yellow]{tr('total_providers', lang)}: {len(providers)}[/]",
            title=f"[cyan]{tr('providers_title', lang)}[/]",
            border_style="yellow",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Provider list error: {e}")
        console.print(f"[red]❌ {tr('model_error', lang)}[/]")

def system_status(user_id: str) -> None:
    """Show system status"""
    lang = get_user_lang(user_id)
    try:
        models_dict = get_supported_models()
        total_models = sum(len(m) for m in models_dict.values())
        providers = init_providers()
        user_models = load_user_models()
        current_model = user_models.get(str(user_id), 'gpt-4o')
        last_active = time.strftime(tr('time_format', lang), time.localtime(stats['last_activity']))
        api_type = tr('using_client_api', lang) if USE_CLIENT_API else tr('using_legacy_api', lang)
        console.print(Panel(
            f"[bold]{tr('current_model', lang)}:[/] {current_model}\n"
            f"[bold]{tr('available_models', lang)}:[/] {total_models}\n"
            f"[bold]{tr('active_providers', lang)}:[/] {len(providers)}\n"
            f"[bold]{tr('active_chats', lang)}:[/] {stats['active_chats']}\n"
            f"[bold]{tr('total_messages', lang)}:[/] {stats['total_messages']}\n"
            f"[bold]{tr('saved_blocks', lang)}:[/] {stats['saved_code_blocks']}\n"
            f"[bold]{tr('api_calls', lang)}:[/] {stats['total_api_calls']}\n"
            f"[bold]{tr('last_activity', lang)}:[/] {last_active}\n"
            f"[bold]System:[/] {sys.platform}\n"
            f"[bold]Python:[/] {sys.version.split()[0]}\n"
            f"[bold]API:[/] {api_type}",
            title=f"[cyan]{tr('system_status_title', lang)}[/]",
            border_style="green",
            padding=(1, 2),
            width=70
        ))
    except Exception as e:
        logger.error(f"Status error: {e}")
        console.print(f"[red]❌ {tr('gen_error', lang)}[/]")

def show_stats(user_id: str) -> None:
    """Show usage statistics"""
    lang = get_user_lang(user_id)
    try:
        last_active = time.strftime(tr('time_format', lang), time.localtime(stats['last_activity']))
        console.print(Panel(
            f"[bold]{tr('total_messages', lang)}:[/] {stats['total_messages']}\n"
            f"[bold]{tr('saved_blocks', lang)}:[/] {stats['saved_code_blocks']}\n"
            f"[bold]{tr('active_chats', lang)}:[/] {stats['active_chats']}\n"
            f"[bold]{tr('api_calls', lang)}:[/] {stats['total_api_calls']}\n"
            f"[bold]{tr('last_activity', lang)}:[/] {last_active}",
            title=f"[cyan]{tr('stats_title', lang)}[/]",
            border_style="blue",
            padding=(1, 2),
            width=60
        ))
    except Exception as e:
        logger.error(f"Stats error: {e}")
        console.print(f"[red]❌ {tr('gen_error', lang)}[/]")

def chat_loop() -> None:
    """Main chat loop"""
    user_id = "1"  # Single user for console version
    lang = get_user_lang(user_id)
    os.makedirs(os.path.join(CONFIG_DIR, "saved_code"), exist_ok=True)
    # Initialize chats
    chats = load_user_chats()
    user_chats = chats.setdefault(user_id, {})
    active_id = user_chats.get("active")
    if not active_id or active_id not in user_chats.get("chats", {}):
        active_id = new_chat(user_id)
    # Welcome message
    g4f_version = getattr(g4f, 'version', 'unknown')
    api_type = tr('using_client_api', lang) if USE_CLIENT_API else tr('using_legacy_api', lang)
    console.print(Panel(
        f"[bold cyan]{tr('welcome', lang)}[/] (g4f v{G4F_VERSION})\n"
        f"[dim]{api_type}[/]\n"
        f"[bold]{tr('developer', lang)}:[/] AiTechnologyDev\n"
        f"[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]",
        title=f"[cyan]AI Chat Console[/]",
        border_style="bright_cyan",
        padding=(1, 4),
        width=80
    ))
    show_help(user_id)
    init_providers()
    # Main interaction loop
    while True:
        try:
            console.print(f"\n[bold cyan]{tr('chat_prompt', lang)}:[/] ", end="")
            user_input = input().strip()
            if not user_input:
                continue
            # Update stats
            stats['total_messages'] += 1
            stats['last_activity'] = time.time()
            # Command handling
            if user_input.startswith('/'):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1] if len(cmd_parts) > 1 else None
                if cmd == '/exit':
                    console.print(f"[bold yellow]{tr('exit_confirmation', lang)}[/]")
                    break
                elif cmd == '/help':
                    show_help(user_id)
                elif cmd == '/newchat':
                    active_id = new_chat(user_id)
                elif cmd == '/usechat':
                    if arg:
                        if use_chat(user_id, arg):
                            active_id = arg
                    else:
                        console.print(f"[red]❌ Usage: /usechat <chat_id>[/]")
                elif cmd == '/delchat':
                    if arg:
                        del_chat(user_id, arg)
                    else:
                        console.print(f"[red]❌ Usage: /delchat <chat_id>[/]")
                elif cmd == '/chats':
                    list_chats(user_id)
                elif cmd == '/setmodel':
                    if arg:
                        set_model(user_id, arg)
                    else:
                        console.print(f"[red]❌ Usage: /setmodel <model_name>[/]")
                elif cmd == '/mymodel':
                    show_model(user_id)
                elif cmd == '/models':
                    list_models(user_id)
                elif cmd == '/providers':
                    list_providers(user_id)
                elif cmd == '/status':
                    system_status(user_id)
                elif cmd == '/lang':
                    if arg and arg in ['en', 'ru']:
                        save_user_lang(user_id, arg)
                        lang = arg
                        console.print(f"[green]✅ {tr('lang_set', lang)}: {arg}[/]")
                    else:
                        console.print(f"[yellow]Current language: {lang}[/]")
                        console.print(f"[red]❌ {tr('invalid_lang', lang)}[/]")
                elif cmd == '/stats':
                    show_stats(user_id)
                else:
                    console.print(f"[red]❌ {tr('unknown_command', lang)}. /help {tr('help', lang).lower()}[/]")
                continue
            # Process user message
            all_chats = load_user_chats()
            user_chats = all_chats.setdefault(user_id, {})
            chat_data = user_chats.setdefault("chats", {}).setdefault(active_id, {})
            history = chat_data.setdefault("history", [])
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            # Generate response with progress indicator
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
                    # Add to history if valid response
                    if response_text and not response_text.startswith("❌"):
                        history.append({"role": "assistant", "content": response_text})
                    # Process thinking patterns
                    response_text = process_model_thinking(response_text, lang)
                    # Save code blocks
                    response_text = save_code_blocks(response_text, active_id, lang)
                    # Display response with syntax highlighting
                    console.print(f"\n[bold cyan]🤖 {tr('ai_prompt', lang)}:[/]")
                    try:
                        highlighted = highlight_code(response_text)
                        console.print(highlighted)
                    except:
                        console.print(response_text)
                except Exception as e:
                    logger.error(f"Generation error: {e}")
                    console.print(f"\n[red]⚠️ {tr('gen_error', lang)}[/]")
                progress.update(task, completed=100)
            # Save updated chat history
            save_user_chats(all_chats)
        except KeyboardInterrupt:
            console.print(f"\n[bold yellow]{tr('exit', lang)}: /exit[/]")
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            console.print(f"[red]⚠️ {tr('main_error', lang)}[/]")

if __name__ == '__main__':
    chat_loop()