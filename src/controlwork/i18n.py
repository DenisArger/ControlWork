from __future__ import annotations

import random

from .themed_quotes_data import BASE_THEMED_QUOTES
from .quote_models import ThemedQuote

TEXTS = {
    "en": {
        "app_title": "ControlWork",
        "menu_status": "Status",
        "menu_pause": "Pause",
        "menu_resume": "Resume",
        "menu_break_now": "Take a break now",
        "menu_stats": "Statistics",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "state_active": "Active",
        "state_idle": "Idle",
        "state_break": "Break",
        "state_paused": "Paused",
        "tab_status": "Status",
        "tab_settings": "Settings",
        "tab_stats": "Statistics",
        "status_title": "Current state",
        "status_work_time": "Work time",
        "status_until_break": "Until break",
        "status_no_break": "not scheduled",
        "today_active": "Active today",
        "today_idle": "Idle today",
        "today_break": "Break today",
        "today_snooze": "Snoozes today",
        "today_skip": "Skips today",
        "settings_language": "Language",
        "settings_autostart": "Start with system",
        "settings_idle": "Idle threshold (sec)",
        "settings_break": "Break duration (min)",
        "settings_tone": "Reminder tone",
        "settings_soft": "Soft points (min, comma)",
        "settings_hard": "Hard points (min, comma)",
        "settings_reset": "Workday reset (HH:MM)",
        "settings_learning_json": "Learning JSON files",
        "settings_browse": "Browse...",
        "settings_save": "Save settings",
        "saved_ok": "Settings saved",
        "learning_json_invalid": "Learning JSON file is invalid. Continuing with quotes and irregular verbs.",
        "learning_json_unavailable": "Learning JSON file is unavailable. Continuing with quotes and irregular verbs.",
        "learning_example_prefix": "Example",
        "learning_example_translation_prefix": "Example translation",
        "learning_transcription_prefix": "Transcription",
        "btn_snooze": "Snooze 5 min",
        "btn_ignore": "Close",
        "btn_cancel": "Cancel",
        "overlay_start": "Start break now",
        "overlay_skip": "Skip",
        "overlay_continue": "Continue work",
        "overlay_snooze": "Snooze 5 min",
        "overlay_remaining": "Remaining: {seconds}s",
        "overlay_idle": "Idle streak: {seconds}s / 120s",
        "break_shortened": "Break shortened, back to work",
        "limit_snooze": "Snooze limit reached (2 per work hour)",
        "limit_skip": "Skip limit reached (1 per day)",
        "first_run_title": "Initial setup",
        "first_run_apply": "Apply",
        "first_run_soft_hint": "Example: 15,30,45",
        "first_run_hard_hint": "Example: 50",
        "parse_error": "Cannot parse points list",
        "tone_friendly": "Friendly",
        "tone_care": "Caring",
        "tone_neutral": "Neutral",
        "tone_motivation": "Motivational",
        "tone_short": "Short",
        "btn_hide_quotes": "Hide block",
        "btn_show_quotes": "Show block",
        "learning_block_title": "Now showing",
        "quote_topic_irregular": "Irregular Verbs",
        "quote_topic_family": "Family",
        "quote_topic_discipline": "Discipline",
        "quote_topic_health": "Health",
        "quote_topic_children": "Children",
        "quote_topic_leadership": "Leadership",
        "quote_topic_bible": "Bible",
        "quote_topic_custom_json": "Custom English",
    },
    "ru": {
        "app_title": "ControlWork",
        "menu_status": "Статус",
        "menu_pause": "Пауза",
        "menu_resume": "Продолжить",
        "menu_break_now": "Сделать перерыв сейчас",
        "menu_stats": "Статистика",
        "menu_settings": "Настройки",
        "menu_exit": "Выход",
        "state_active": "Работа",
        "state_idle": "Нет активности",
        "state_break": "Перерыв",
        "state_paused": "Пауза",
        "tab_status": "Статус",
        "tab_settings": "Настройки",
        "tab_stats": "Статистика",
        "status_title": "Текущее состояние",
        "status_work_time": "Время работы",
        "status_until_break": "До перерыва",
        "status_no_break": "не запланирован",
        "today_active": "Активно сегодня",
        "today_idle": "Неактивно сегодня",
        "today_break": "Перерыв сегодня",
        "today_snooze": "Отложено сегодня",
        "today_skip": "Пропусков сегодня",
        "settings_language": "Язык",
        "settings_autostart": "Запускать с системой",
        "settings_idle": "Порог idle (сек)",
        "settings_break": "Длительность перерыва (мин)",
        "settings_tone": "Стиль напоминаний",
        "settings_soft": "Мягкие точки (мин, через запятую)",
        "settings_hard": "Строгие точки (мин, через запятую)",
        "settings_reset": "Сброс рабочего дня (ЧЧ:ММ)",
        "settings_learning_json": "JSON-файлы для обучения",
        "settings_browse": "Выбрать...",
        "settings_save": "Сохранить настройки",
        "saved_ok": "Настройки сохранены",
        "learning_json_invalid": "JSON-файл обучения невалиден. Продолжаем с цитатами и неправильными глаголами.",
        "learning_json_unavailable": "JSON-файл обучения недоступен. Продолжаем с цитатами и неправильными глаголами.",
        "learning_example_prefix": "Пример",
        "learning_example_translation_prefix": "Перевод примера",
        "learning_transcription_prefix": "Транскрипция",
        "btn_snooze": "Отложить 5 мин",
        "btn_ignore": "Закрыть",
        "btn_cancel": "Отмена",
        "overlay_start": "Начать перерыв",
        "overlay_skip": "Пропустить",
        "overlay_continue": "Продолжить работу",
        "overlay_snooze": "Отложить 5 мин",
        "overlay_remaining": "Осталось: {seconds}с",
        "overlay_idle": "Idle-серия: {seconds}с / 120с",
        "break_shortened": "Перерыв сокращен, возвращаемся к работе",
        "limit_snooze": "Лимит отложений исчерпан (2 в рабочий час)",
        "limit_skip": "Лимит пропусков исчерпан (1 в день)",
        "first_run_title": "Первичная настройка",
        "first_run_apply": "Применить",
        "first_run_soft_hint": "Например: 15,30,45",
        "first_run_hard_hint": "Например: 50",
        "parse_error": "Не удалось разобрать список точек",
        "tone_friendly": "Дружелюбный",
        "tone_care": "Заботливый",
        "tone_neutral": "Нейтральный",
        "tone_motivation": "Мотивационный",
        "tone_short": "Короткий",
        "btn_hide_quotes": "Скрыть блок",
        "btn_show_quotes": "Показать блок",
        "learning_block_title": "Сейчас показываем",
        "quote_topic_irregular": "Неправильные глаголы",
        "quote_topic_family": "Семья",
        "quote_topic_discipline": "Дисциплина",
        "quote_topic_health": "Здоровье",
        "quote_topic_children": "Дети",
        "quote_topic_leadership": "Лидерство",
        "quote_topic_bible": "Библейские",
        "quote_topic_custom_json": "Свой английский",
    },
}


TONE_MESSAGE_KEYS = {
    "soft_title",
    "soft_body",
    "soft_dialog",
    "hard_title",
    "hard_body",
    "overlay_prompt",
    "break_done",
}

QUOTE_MESSAGE_KEYS = {
    "soft_body",
    "hard_body",
    "overlay_prompt",
    "break_done",
}

QUOTES = {
    "ru": [
        "Маленький шаг каждый день дает большой результат.",
        "Система побеждает мотивацию, когда день сложный.",
        "Фокус любит порядок, а порядок любит паузу.",
        "Делай важное сначала, срочное потом.",
        "Стабильность сильнее идеального рывка.",
        "Глубокая работа начинается с тишины.",
        "Дисциплина - это забота о будущем себе.",
        "Передышка - часть продуктивности, а не ее враг.",
        "Лучше медленно и регулярно, чем редко и героически.",
        "Качество рождается в спокойном темпе.",
        "Чистая голова принимает точные решения.",
        "Твоя энергия - главный рабочий актив.",
        "Пауза сейчас экономит ошибки позже.",
        "Прогресс любит ритм.",
        "Нагрузка без восстановления ведет к шуму вместо результата.",
        "Сильный день строится из коротких фокус-блоков.",
        "Ты управляешь задачами, когда управляешь вниманием.",
        "Отдых - это инвестиция в ясность.",
        "Сначала дыхание, потом ускорение.",
        "Один завершенный шаг лучше десяти начатых.",
        "Результат растет там, где есть повторяемость.",
        "Сфокусируйся на процессе - итог подтянется.",
        "Пределы делают темп устойчивым.",
        "Пауза возвращает точность мышления.",
        "Сделано вовремя лучше, чем идеально когда-нибудь.",
        "Внимание - это ресурс, расходуй его осознанно.",
        "Спокойный ритм удерживает длинную дистанцию.",
        "Побеждает не самый быстрый, а самый последовательный.",
        "Восстановление - часть профессионализма.",
        "Чем яснее приоритет, тем легче движение вперед.",
    ],
    "en": [
        "Small daily steps create big outcomes.",
        "Systems beat motivation on hard days.",
        "Focus needs structure, and structure needs breaks.",
        "Do what matters first, then what is loud.",
        "Consistency beats perfect bursts.",
        "Deep work starts with quiet.",
        "Discipline is care for your future self.",
        "Rest is part of productivity, not its enemy.",
        "Steady beats heroic and rare.",
        "Quality grows in a calm pace.",
        "Clear mind, better decisions.",
        "Your energy is your core work asset.",
        "A break now prevents mistakes later.",
        "Progress loves rhythm.",
        "No recovery means noise instead of results.",
        "Strong days are built from short focus blocks.",
        "You manage tasks by managing attention.",
        "Rest is an investment in clarity.",
        "Breathe first, accelerate second.",
        "One finished step beats ten started ones.",
        "Results grow where repetition exists.",
        "Trust the process and outcomes follow.",
        "Limits make pace sustainable.",
        "Pauses restore precision of thought.",
        "Done on time beats perfect someday.",
        "Attention is a resource, spend it intentionally.",
        "Calm rhythm wins long distance.",
        "The consistent one wins the race.",
        "Recovery is part of professionalism.",
        "Clear priorities make forward motion easier.",
    ],
}
@dataclass(frozen=True)
class IrregularVerb:
    base: str
    past: str
    past_participle: str
    translation: str


THEMED_QUOTES: dict[str, dict[str, list[ThemedQuote]]] = BASE_THEMED_QUOTES

IRREGULAR_VERBS: dict[str, list[IrregularVerb]] = {
    "ru": [
        IrregularVerb("be", "was/were", "been", "быть"),
        IrregularVerb("begin", "began", "begun", "начинать"),
        IrregularVerb("break", "broke", "broken", "ломать"),
        IrregularVerb("bring", "brought", "brought", "приносить"),
        IrregularVerb("build", "built", "built", "строить"),
        IrregularVerb("buy", "bought", "bought", "покупать"),
        IrregularVerb("choose", "chose", "chosen", "выбирать"),
        IrregularVerb("come", "came", "come", "приходить"),
        IrregularVerb("do", "did", "done", "делать"),
        IrregularVerb("drink", "drank", "drunk", "пить"),
        IrregularVerb("drive", "drove", "driven", "водить"),
        IrregularVerb("eat", "ate", "eaten", "есть"),
        IrregularVerb("feed", "fed", "fed", "кормить"),
        IrregularVerb("feel", "felt", "felt", "чувствовать"),
        IrregularVerb("find", "found", "found", "находить"),
        IrregularVerb("forget", "forgot", "forgotten", "забывать"),
        IrregularVerb("get", "got", "got", "получать"),
        IrregularVerb("give", "gave", "given", "давать"),
        IrregularVerb("go", "went", "gone", "идти"),
        IrregularVerb("have", "had", "had", "иметь"),
        IrregularVerb("hold", "held", "held", "держать (в руке)"),
        IrregularVerb("keep", "kept", "kept", "содержать, хранить"),
        IrregularVerb("know", "knew", "known", "знать"),
        IrregularVerb("leave", "left", "left", "покидать"),
        IrregularVerb("make", "made", "made", "делать/создавать"),
        IrregularVerb("mean", "meant", "meant", "означать"),
        IrregularVerb("meet", "met", "met", "встречать"),
        IrregularVerb("read", "read", "read", "читать"),
        IrregularVerb("run", "ran", "run", "бежать"),
        IrregularVerb("say", "said", "said", "говорить"),
        IrregularVerb("see", "saw", "seen", "видеть"),
        IrregularVerb("sleep", "slept", "slept", "спать"),
        IrregularVerb("speak", "spoke", "spoken", "говорить"),
        IrregularVerb("sweep", "swept", "swept", "подметать"),
        IrregularVerb("take", "took", "taken", "брать"),
        IrregularVerb("think", "thought", "thought", "думать"),
        IrregularVerb("deal", "dealt", "dealt", "иметь дело с"),
        IrregularVerb("become", "became", "become", "становиться"),
        IrregularVerb("blow", "blew", "blown", "дуть"),
        IrregularVerb("draw", "drew", "drawn", "рисовать"),
        IrregularVerb("fly", "flew", "flown", "летать"),
        IrregularVerb("grow", "grew", "grown", "расти"),
        IrregularVerb("ring", "rang", "rung", "звонить, звенеть"),
        IrregularVerb("show", "showed", "shown", "показывать"),
        IrregularVerb("sing", "sang", "sung", "петь"),
        IrregularVerb("sink", "sank", "sunk", "тонуть"),
        IrregularVerb("swim", "swam", "swum", "плавать"),
        IrregularVerb("throw", "threw", "thrown", "бросать"),
        IrregularVerb("wear", "wore", "worn", "носить"),
        IrregularVerb("write", "wrote", "written", "писать"),
        IrregularVerb("win", "won", "won", "побеждать"),
    ],
    "en": [
        IrregularVerb("be", "was/were", "been", "to exist"),
        IrregularVerb("begin", "began", "begun", "start"),
        IrregularVerb("break", "broke", "broken", "separate into pieces"),
        IrregularVerb("bring", "brought", "brought", "carry to a place"),
        IrregularVerb("build", "built", "built", "construct"),
        IrregularVerb("buy", "bought", "bought", "purchase"),
        IrregularVerb("choose", "chose", "chosen", "select"),
        IrregularVerb("come", "came", "come", "move toward"),
        IrregularVerb("do", "did", "done", "perform"),
        IrregularVerb("drink", "drank", "drunk", "consume liquid"),
        IrregularVerb("drive", "drove", "driven", "operate a vehicle"),
        IrregularVerb("eat", "ate", "eaten", "consume food"),
        IrregularVerb("feed", "fed", "fed", "give food to"),
        IrregularVerb("feel", "felt", "felt", "sense"),
        IrregularVerb("find", "found", "found", "discover"),
        IrregularVerb("forget", "forgot", "forgotten", "fail to remember"),
        IrregularVerb("get", "got", "got", "obtain"),
        IrregularVerb("give", "gave", "given", "provide"),
        IrregularVerb("go", "went", "gone", "move"),
        IrregularVerb("have", "had", "had", "possess"),
        IrregularVerb("hold", "held", "held", "grip"),
        IrregularVerb("keep", "kept", "kept", "retain"),
        IrregularVerb("know", "knew", "known", "be aware of"),
        IrregularVerb("leave", "left", "left", "go away"),
        IrregularVerb("make", "made", "made", "create"),
        IrregularVerb("mean", "meant", "meant", "signify"),
        IrregularVerb("meet", "met", "met", "encounter"),
        IrregularVerb("read", "read", "read", "interpret text"),
        IrregularVerb("run", "ran", "run", "move fast"),
        IrregularVerb("say", "said", "said", "speak words"),
        IrregularVerb("see", "saw", "seen", "perceive visually"),
        IrregularVerb("sleep", "slept", "slept", "rest"),
        IrregularVerb("speak", "spoke", "spoken", "talk"),
        IrregularVerb("sweep", "swept", "swept", "clean with a broom"),
        IrregularVerb("take", "took", "taken", "carry"),
        IrregularVerb("think", "thought", "thought", "consider"),
        IrregularVerb("deal", "dealt", "dealt", "handle"),
        IrregularVerb("become", "became", "become", "turn into"),
        IrregularVerb("blow", "blew", "blown", "send out air"),
        IrregularVerb("draw", "drew", "drawn", "sketch"),
        IrregularVerb("fly", "flew", "flown", "move through air"),
        IrregularVerb("grow", "grew", "grown", "increase"),
        IrregularVerb("ring", "rang", "rung", "sound"),
        IrregularVerb("show", "showed", "shown", "display"),
        IrregularVerb("sing", "sang", "sung", "perform with voice"),
        IrregularVerb("sink", "sank", "sunk", "go down below surface"),
        IrregularVerb("swim", "swam", "swum", "move in water"),
        IrregularVerb("throw", "threw", "thrown", "send through air"),
        IrregularVerb("wear", "wore", "worn", "have clothing on"),
        IrregularVerb("write", "wrote", "written", "produce text"),
        IrregularVerb("win", "won", "won", "be victorious"),
    ],
}


def random_thematic_quote(lang: str, previous: ThemedQuote | None = None) -> ThemedQuote:
    lang_key = "en" if lang == "en" else "ru"
    pool = [quote for topic_quotes in THEMED_QUOTES[lang_key].values() for quote in topic_quotes]
    if previous is not None:
        filtered = [quote for quote in pool if quote != previous]
        if filtered:
            pool = filtered
    return random.choice(pool)


def random_irregular_verb(lang: str, previous: IrregularVerb | None = None) -> IrregularVerb:
    lang_key = "en" if lang == "en" else "ru"
    pool = IRREGULAR_VERBS[lang_key]
    if previous is not None:
        filtered = [verb for verb in pool if verb != previous]
        if filtered:
            pool = filtered
    return random.choice(pool)


def format_thematic_quote_author(quote: ThemedQuote) -> str:
    if quote.translation is not None and quote.translation.lower() == "nrp":
        return f"{quote.author} (НРП)"
    return quote.author


TONE_TEXTS = {
    "ru": {
        "friendly": {
            "soft_title": "Фокус в деле",
            "soft_body": "{minutes} минут отличной работы. Цитата: «{quote}»",
            "soft_dialog": "Сделаем паузу и вернемся с ясной головой?",
            "hard_title": "Время обязательного отдыха",
            "hard_body": "Вы долго в концентрации. Сейчас нужен перерыв. Цитата: «{quote}»",
            "overlay_prompt": "Пауза на восстановление. Цитата: «{quote}»",
            "break_done": "Перерыв завершен. Цитата: «{quote}»",
        },
        "care": {
            "soft_title": "Бережем энергию",
            "soft_body": "{minutes} минут подряд. Пора дать телу отдых. Цитата: «{quote}»",
            "soft_dialog": "Небольшая пауза сейчас сделает следующий рабочий блок легче.",
            "hard_title": "Нужен перерыв",
            "hard_body": "Порог непрерывной работы достигнут. Переключаемся на отдых. Цитата: «{quote}»",
            "overlay_prompt": "Сделайте паузу для восстановления. Цитата: «{quote}»",
            "break_done": "Вы восстановились. Цитата: «{quote}»",
        },
        "neutral": {
            "soft_title": "Напоминание о паузе",
            "soft_body": "Активная работа: {minutes} минут. Цитата: «{quote}»",
            "soft_dialog": "Рекомендуется сделать короткий перерыв.",
            "hard_title": "Обязательный перерыв",
            "hard_body": "Достигнут максимальный интервал без отдыха. Цитата: «{quote}»",
            "overlay_prompt": "Начните перерыв сейчас. Цитата: «{quote}»",
            "break_done": "Перерыв засчитан. Цитата: «{quote}»",
        },
        "motivation": {
            "soft_title": "Отличный темп",
            "soft_body": "{minutes} минут продуктивности. Пауза сохранит темп. Цитата: «{quote}»",
            "soft_dialog": "Делаем короткий перерыв и возвращаемся еще сильнее?",
            "hard_title": "Перезагрузка обязательна",
            "hard_body": "Чтобы сохранить концентрацию, нужен перерыв прямо сейчас. Цитата: «{quote}»",
            "overlay_prompt": "Время на перезагрузку. Цитата: «{quote}»",
            "break_done": "Супер, перерыв выполнен. Цитата: «{quote}»",
        },
        "short": {
            "soft_title": "Пауза?",
            "soft_body": "{minutes} минут без остановки. Цитата: «{quote}»",
            "soft_dialog": "Короткий отдых и обратно в поток.",
            "hard_title": "Стоп, отдых",
            "hard_body": "Пора сделать обязательную паузу. Цитата: «{quote}»",
            "overlay_prompt": "Сейчас перерыв. Цитата: «{quote}»",
            "break_done": "Готово. Цитата: «{quote}»",
        },
    },
    "en": {
        "friendly": {
            "soft_title": "Focus in Motion",
            "soft_body": "{minutes} minutes of solid work. Quote: \"{quote}\"",
            "soft_dialog": "Take a short pause and return with a clear head?",
            "hard_title": "Mandatory Recovery Time",
            "hard_body": "You have worked in deep focus for a long stretch. Quote: \"{quote}\"",
            "overlay_prompt": "Pause and recharge now. Quote: \"{quote}\"",
            "break_done": "Break completed. Quote: \"{quote}\"",
        },
        "care": {
            "soft_title": "Protect Your Energy",
            "soft_body": "{minutes} minutes in a row. Quote: \"{quote}\"",
            "soft_dialog": "A short pause now will make the next block easier.",
            "hard_title": "Break Needed",
            "hard_body": "Continuous work threshold reached. Quote: \"{quote}\"",
            "overlay_prompt": "Take a recovery pause. Quote: \"{quote}\"",
            "break_done": "Recovered and ready. Quote: \"{quote}\"",
        },
        "neutral": {
            "soft_title": "Break reminder",
            "soft_body": "Active work: {minutes} minutes. Quote: \"{quote}\"",
            "soft_dialog": "A short break is recommended.",
            "hard_title": "Mandatory break",
            "hard_body": "Maximum uninterrupted work interval reached. Quote: \"{quote}\"",
            "overlay_prompt": "Start break now. Quote: \"{quote}\"",
            "break_done": "Break counted. Quote: \"{quote}\"",
        },
        "motivation": {
            "soft_title": "Great momentum",
            "soft_body": "{minutes} minutes of productive work. Quote: \"{quote}\"",
            "soft_dialog": "Take a short break and come back stronger?",
            "hard_title": "Reset required",
            "hard_body": "To keep high focus, start a break now. Quote: \"{quote}\"",
            "overlay_prompt": "Time to reset. Quote: \"{quote}\"",
            "break_done": "Nice reset complete. Quote: \"{quote}\"",
        },
        "short": {
            "soft_title": "Pause?",
            "soft_body": "{minutes} minutes nonstop. Quote: \"{quote}\"",
            "soft_dialog": "Short break, then back to flow.",
            "hard_title": "Stop, rest",
            "hard_body": "Mandatory pause time. Quote: \"{quote}\"",
            "overlay_prompt": "Break now. Quote: \"{quote}\"",
            "break_done": "Done. Quote: \"{quote}\"",
        },
    },
}

def random_quote(lang: str) -> str:
    lang_key = "en" if lang == "en" else "ru"
    return random.choice(QUOTES[lang_key])


def tr(lang: str, key: str, **kwargs: object) -> str:
    tone = str(kwargs.pop("_tone", "friendly"))
    lang_key = "en" if lang == "en" else "ru"

    text = None
    if key in TONE_MESSAGE_KEYS:
        text = TONE_TEXTS.get(lang_key, {}).get(tone, {}).get(key)
        if text is None:
            text = TONE_TEXTS.get(lang_key, {}).get("friendly", {}).get(key)

    if text is None:
        text = TEXTS.get(lang_key, TEXTS["ru"]).get(key, key)

    if key in QUOTE_MESSAGE_KEYS and "quote" not in kwargs:
        kwargs["quote"] = random_quote(lang_key)

    if kwargs:
        return text.format(**kwargs)
    return text
