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

# Настройка логирования в файл
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

MODEL_FILE = 'user_models.json'
USER_CHATS_FILE = 'user_chats.json'

# Кэширование данных
user_models_cache = {}
user_chats_cache = {}
active_providers = []
provider_classes = {}

# Глобальная блокировка для потокобезопасности
cache_lock = Lock()

# Черный список провайдеров
BLACKLISTED_PROVIDERS = ['BlackForestLabs_Flux1Dev', 'DeepInfra', 'FlowGpt', 'Free2GPT', 'ImageLabs', 'HuggingFace']

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
            
        logger.info("Инициализация провайдеров...")
        with console.status("[bold blue]Инициализация провайдеров...[/]", spinner="dots"):
            all_providers = get_all_providers()
            active_providers = []
            provider_classes = {}
            
            for provider in all_providers:
                try:
                    provider_name = provider.__name__
                    
                    if provider_name in BLACKLISTED_PROVIDERS:
                        logger.info(f"Пропускаем заблокированный провайдер: {provider_name}")
                        continue
                    
                    if (hasattr(provider, 'working') and provider.working and (hasattr(provider, 'url') or hasattr(provider, 'model'))):
                        active_providers.append(provider)
                        provider_classes[provider_name] = provider
                        logger.info(f"Добавлен провайдер: {provider_name}")
                except Exception as e:
                    logger.warning(f"Ошибка проверки {provider.__name__}: {str(e)[:100]}")
            
            if not active_providers:
                backup_providers = [g4f.Provider.You]
                for provider in backup_providers:
                    if provider.__name__ not in BLACKLISTED_PROVIDERS:
                        active_providers.append(provider)
                        provider_classes[provider.__name__] = provider
                logger.warning(f"Используем резервные провайдеры: {[p.__name__ for p in active_providers]}")
            
            logger.info(f"Активных провайдеров: {len(active_providers)}")
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
            logger.error(f"Ошибка загрузки моделей: {e}")
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
            logger.error(f"Ошибка сохранения моделей: {e}")

# Загрузка чатов
def load_user_chats():
    global user_chats_cache
    with cache_lock:
        if user_chats_cache:
            return user_chats_cache
            
        try:
            if os.path.exists(USER_CHATS_FILE):
                with open(USER_CHATS_FILE, 'r', encoding='utf-8') as f:
                    user_chats_cache = json.load(f)
            else:
                user_chats_cache = {}
        except Exception as e:
            logger.error(f"Ошибка загрузки чатов: {e}")
            user_chats_cache = {}
        return user_chats_cache

# Сохранение чатов
def save_user_chats(data):
    global user_chats_cache
    with cache_lock:
        user_chats_cache = data
        try:
            with open(USER_CHATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения чатов: {e}")

# Полный список моделей
def get_supported_models():
    return [
        "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", 
        "o1", "o1-mini", "o3-mini", "o3", "o3-mini-hight", 
        "o4-mini", "o4-mini-hight", "gpt-4.1", "gpt-4.1-mini", 
        "gpt-4.1-nano", "gpt-4.5", "llama-2-7b", "llama-2-70b", 
        "llama-3-8b", "llama-3.1-8b", "llama-3.1-70b", "llama-3.1-405b", 
        "llama-3.2-1b", "llama-3.2-3b", "llama-3.2-11b", "llama-3.3-70b", 
        "llama-3.2-90b", "mistral-7b", "mixtral-8x7b", "mistral-nemo", 
        "mistral-small-24b", "phi-4", "gemini-1.5-flash", "gemini-1.5-pro", 
        "gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro", 
        "qwen-1.5-7b", "qwen-2-72b", "qwen-2.5", "qwen-2.5-7b", 
        "qwen-2.5-72b", "qwen-2.5-coder-32b", "qwen-3-32b", "qwen-3-30b", 
        "qwq-32b", "deepseek-v3", "deepseek-r1", "grok-3", "sonar-pro", 
        "sonar", "sonar-reasoning", "sonar-reasoning-pro", "claude-3.5-sonnet", 
        "claude-3-opus", "claude-3-sonnet", "claude-3-haiku", 
    ]

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
                logger.info(f"Используем сохраненный провайдер: {saved_provider}")
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
            logger.warning(f"Ошибка в сохраненном провайдере: {error_msg}")
            chat_data["provider"] = None
            user_chats.setdefault("chats", {})[chat_id] = chat_data
            all_chats[str(user_id)] = user_chats
            save_user_chats(all_chats)

    # Пробуем все доступные провайдеры
    for provider in providers:
        try:
            if saved_provider and provider.__name__ == saved_provider:
                continue
                
            logger.info(f"Пробуем провайдер: {provider.__name__}")
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
            logger.warning(f"Ошибка в провайдере: {error_msg}")
            time.sleep(0.1)
    
    error_details = "\n".join(provider_errors[-5:])
    return f"⚠️ Все провайдеры недоступны. Попробуйте позже или смените модель.\n\nОшибки:\n{error_details}"

# Обработка размышлений модели
def process_model_thinking(response_text):
    thinking_pattern = r'<thinking>(.*?)</thinking>'
    matches = re.findall(thinking_pattern, response_text, re.DOTALL)
    
    if matches:
        console.print("\n[bold yellow]💭 Размышления модели:[/]")
        for i, thought in enumerate(matches, 1):
            thought = thought.strip()
            if thought:
                console.print(f"[dim]{i}.[/] {thought}")
        
        response_text = re.sub(thinking_pattern, '', response_text, flags=re.DOTALL).strip()
    
    return response_text

# Показать справку
def show_help():
    console.print(Panel(
        "[bold cyan]🤖 Консольный AI Чат (g4f v0.5.7.5)[/]\n"
        "[bold]Разработчик:[/] AiTechnologyDev\n"
        "[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]\n\n"
        "[bold]Команды:[/]\n"
        "  [bold]/newchat[/]  - создать новый чат\n"
        "  [bold]/usechat[/]  - переключить чат\n"
        "  [bold]/delchat[/]  - удалить чат\n"
        "  [bold]/chats[/]    - список чатов\n"
        "  [bold]/setmodel[/] - установить модель\n"
        "  [bold]/mymodel[/]  - текущая модель\n"
        "  [bold]/models[/]   - доступные модели\n"
        "  [bold]/providers[/]- доступные провайдеры\n"
        "  [bold]/status[/]   - статус системы\n"
        "  [bold]/exit[/]     - выход из программы\n"
        "  [bold]/help[/]     - показать справку\n\n"
        "[bold]Просто введите текст для общения с ИИ[/]",
        title="Помощь",
        title_align="left",
        border_style="cyan",
        padding=(1, 2)
    ))

# Установка модели
def set_model(user_id, model_name):
    try:
        supported_models = get_supported_models()
        
        if model_name not in supported_models:
            console.print(f"[red]❌ Модель недоступна. Используйте /models для списка[/]")
            return False
        
        user_models = load_user_models()
        user_models[str(user_id)] = model_name
        save_user_models(user_models)
        
        console.print(f"[green]✅ Модель установлена:[/] [bold]{model_name}[/]")
        return True
    except Exception as e:
        logger.error(f"Ошибка установки модели: {e}")
        console.print("[red]❌ Ошибка установки модели[/]")
        return False

# Создание нового чата
def new_chat(user_id):
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    chat_id = str(uuid.uuid4())[:8]
    
    chat_list[chat_id] = {
        "history": [{"role": "system", "content": "Вы дружелюбный и полезный AI ассистент."}],
        "provider": None
    }
    
    user_chats["chats"] = chat_list
    user_chats["active"] = chat_id
    chats[user_id] = user_chats
    save_user_chats(chats)
    console.print(f"[green]🆕 Новый чат создан и выбран:[/] [bold]{chat_id}[/]")
    return chat_id

# Переключение чата
def use_chat(user_id, chat_id):
    try:
        user_id = str(user_id)
        chats = load_user_chats()
        user_chats = chats.get(user_id, {})
        chat_list = user_chats.get("chats", {})
        if chat_id in chat_list:
            user_chats["active"] = chat_id
            chats[user_id] = user_chats
            save_user_chats(chats)
            console.print(f"[green]✅ Переключено на чат:[/] [bold]{chat_id}[/]")
            return True
        else:
            console.print("[red]❌ Чат с таким ID не найден.[/]")
            return False
    except Exception:
        console.print("[red]❌ Ошибка переключения чата[/]")
        return False

# Удаление чата
def del_chat(user_id, chat_id):
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
                        "history": [{"role": "system", "content": "Вы дружелюбный и полезный AI ассистент."}],
                        "provider": None
                    }
                    user_chats["active"] = new_chat_id
            user_chats["chats"] = chat_list
            chats[user_id] = user_chats
            save_user_chats(chats)
            console.print(f"[yellow]🗑️ Чат [bold]{chat_id}[/] удалён.[/]")
            return True
        else:
            console.print("[red]❌ Чат с таким ID не найден.[/]")
            return False
    except Exception:
        console.print("[red]❌ Ошибка удаления чата[/]")
        return False

# Список чатов
def list_chats(user_id):
    user_id = str(user_id)
    chats = load_user_chats()
    user_chats = chats.get(user_id, {})
    chat_list = user_chats.get("chats", {})
    active_id = user_chats.get("active", "default")
    
    if not chat_list:
        console.print("[yellow]У вас пока нет чатов.[/]")
        return
    
    panel_text = ""
    for cid in chat_list:
        mark = "🟢" if cid == active_id else "⚪"
        panel_text += f"[bold]{mark} {cid}[/]\n"
    
    console.print(Panel(
        panel_text.strip(),
        title="[bold cyan]Ваши чаты[/]",
        title_align="left",
        border_style="blue",
        padding=(0, 2)
    ))

# Показать текущую модель
def show_model(user_id):
    try:
        user_models = load_user_models()
        model = user_models.get(str(user_id), 'gpt-4o (по умолчанию)')
        console.print(Panel(
            f"[bold]{model}[/]",
            title="[cyan]Текущая модель[/]",
            title_align="left",
            border_style="green",
            padding=(0, 2)
        ))
    except Exception as e:
        logger.error(f"Ошибка показа модели: {e}")
        console.print("[red]❌ Ошибка получения модели[/]")

# Список моделей
def list_models():
    try:
        models_list = get_supported_models()
        panel_text = "\n".join([f"- [bold]{model}[/]" for model in models_list])
        
        console.print(Panel(
            f"{panel_text}\n\n[bold yellow]Всего: {len(models_list)} моделей[/]",
            title="[cyan]Доступные модели (g4f 0.5.7.5)[/]",
            title_align="left",
            border_style="magenta",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Ошибка списка моделей: {e}")
        console.print("[red]❌ Ошибка получения списка моделей[/]")

# Список провайдеров
def list_providers():
    try:
        providers = init_providers()
        panel_text = "\n".join([f"- [bold]{provider.__name__}[/]" for provider in providers])
        
        console.print(Panel(
            f"{panel_text}\n\n[bold yellow]Всего провайдеров: {len(providers)}[/]",
            title="[cyan]Активные провайдеры[/]",
            title_align="left",
            border_style="yellow",
            padding=(0, 2),
            width=80
        ))
    except Exception as e:
        logger.error(f"Ошибка списка провайдеров: {e}")
        console.print("[red]❌ Ошибка получения списка провайдеров[/]")

# Статус системы
def system_status():
    try:
        console.print(Panel(
            f"[bold]Версия g4f:[/] 0.5.7.5\n"
            f"[bold]Моделей доступно:[/] {len(get_supported_models())}\n"
            f"[bold]Провайдеров активно:[/] {len(init_providers())}\n"
            f"[bold]Пользователей:[/] {len(load_user_models())}\n"
            f"[bold]Время:[/] {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[bold]Система:[/] {sys.platform}",
            title="[cyan]Статус системы[/]",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        ))
    except Exception as e:
        logger.error(f"Ошибка статуса: {e}")
        console.print("[red]❌ Ошибка получения статуса системы[/]")

# Основная функция чата
def chat_loop():
    user_id = 1  # Для консольной версии используем одного пользователя
    chats = load_user_chats()
    user_chats = chats.get(str(user_id), {})
    active_id = user_chats.get("active", None)
    
    # Создаем чат если нет активного
    if not active_id or active_id not in user_chats.get("chats", {}):
        active_id = new_chat(user_id)
    
    show_help()
    
    while True:
        try:
            console.print("\n[bold cyan]Вы:[/] ", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
                
            # Обработка команд
            if user_input.startswith('/'):
                cmd = user_input.split()[0].lower()
                
                if cmd == '/exit':
                    console.print("[bold yellow]Выход из программы...[/]")
                    break
                    
                elif cmd == '/help':
                    show_help()
                    
                elif cmd == '/newchat':
                    active_id = new_chat(user_id)
                    
                elif cmd == '/usechat':
                    if len(user_input.split()) > 1:
                        chat_id = user_input.split()[1].strip()
                        if use_chat(user_id, chat_id):
                            active_id = chat_id
                    else:
                        console.print("[red]❌ Укажите ID чата: /usechat <id>[/]")
                        
                elif cmd == '/delchat':
                    if len(user_input.split()) > 1:
                        chat_id = user_input.split()[1].strip()
                        del_chat(user_id, chat_id)
                    else:
                        console.print("[red]❌ Укажите ID чата: /delchat <id>[/]")
                        
                elif cmd == '/chats':
                    list_chats(user_id)
                    
                elif cmd == '/setmodel':
                    if len(user_input.split()) > 1:
                        model_name = user_input.split(maxsplit=1)[1].strip()
                        set_model(user_id, model_name)
                    else:
                        console.print("[red]❌ Укажите модель: /setmodel <название>[/]")
                        
                elif cmd == '/mymodel':
                    show_model(user_id)
                    
                elif cmd == '/models':
                    list_models()
                    
                elif cmd == '/providers':
                    list_providers()
                    
                elif cmd == '/status':
                    system_status()
                    
                else:
                    console.print("[red]❌ Неизвестная команда. Введите /help для списка команд[/]")
                    
                continue
            
            # Получение истории чата
            all_chats = load_user_chats()
            user_chats = all_chats.get(str(user_id), {})
            chat_data = user_chats.get("chats", {}).get(active_id, {})
            history = chat_data.get("history", [])
            
            # Добавление сообщения пользователя
            user_message = {"role": "user", "content": user_input}
            history.append(user_message)
            history = history
            
            # Обновление истории
            chat_data["history"] = history
            user_chats.setdefault("chats", {})[active_id] = chat_data
            all_chats[str(user_id)] = user_chats
            save_user_chats(all_chats)
            
            # Генерация ответа с прогресс-баром
            response_text = ""
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                transient=True,
                console=console
            ) as progress:
                task = progress.add_task("Генерация ответа...", total=None)
                
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
                    response_text = process_model_thinking(response_text)
                    
                    # Вывод ответа
                    console.print("\n[bold cyan]🤖 ИИ:[/]")
                    try:
                        # Пытаемся отформатировать как Markdown
                        md = Markdown(response_text)
                        console.print(md)
                    except:
                        # Простой вывод в случае ошибки
                        console.print(response_text)
                    
                except Exception as e:
                    logger.error(f"Ошибка генерации: {e}")
                    console.print("\n[red]⚠️ Ошибка генерации ответа. Попробуйте позже.[/]")
                
                progress.update(task, completed=100)
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Для выхода введите /exit[/]")
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            console.print("[red]⚠️ Произошла ошибка. Продолжаем работу...[/]")

if __name__ == '__main__':
    console.print(Panel(
        "[bold cyan]Консольный AI Чат[/] (g4f v0.5.7.5)\n"
        "[bold]Разработчик:[/] AiTechnologyDev\n"
        "[bold]GitHub:[/] [link=https://github.com/AITechnologyDev]https://github.com/AITechnologyDev[/]",
        title="Добро пожаловать",
        title_align="center",
        border_style="bright_cyan",
        padding=(1, 4),
        width=80
    ))
    
    init_providers()
    chat_loop()