from __future__ import annotations

import random
from dataclasses import dataclass

TEXTS = {
    "en": {
        "app_title": "ControlWork",
        "menu_status": "Status",
        "menu_pause": "Pause",
        "menu_resume": "Resume",
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
        "settings_save": "Save settings",
        "saved_ok": "Settings saved",
        "btn_snooze": "Snooze 5 min",
        "btn_ignore": "Close",
        "btn_cancel": "Cancel",
        "overlay_start": "Start break now",
        "overlay_skip": "Skip",
        "overlay_snooze": "Snooze 5 min",
        "overlay_remaining": "Remaining: {seconds}s",
        "overlay_idle": "Idle streak: {seconds}s / 120s",
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
        "quote_topic_family": "Family",
        "quote_topic_discipline": "Discipline",
        "quote_topic_health": "Health",
        "quote_topic_children": "Children",
        "quote_topic_leadership": "Leadership",
        "quote_topic_bible": "Bible",
    },
    "ru": {
        "app_title": "ControlWork",
        "menu_status": "Статус",
        "menu_pause": "Пауза",
        "menu_resume": "Продолжить",
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
        "settings_save": "Сохранить настройки",
        "saved_ok": "Настройки сохранены",
        "btn_snooze": "Отложить 5 мин",
        "btn_ignore": "Закрыть",
        "btn_cancel": "Отмена",
        "overlay_start": "Начать перерыв",
        "overlay_skip": "Пропустить",
        "overlay_snooze": "Отложить 5 мин",
        "overlay_remaining": "Осталось: {seconds}с",
        "overlay_idle": "Idle-серия: {seconds}с / 120с",
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
        "quote_topic_family": "Семья",
        "quote_topic_discipline": "Дисциплина",
        "quote_topic_health": "Здоровье",
        "quote_topic_children": "Дети",
        "quote_topic_leadership": "Лидерство",
        "quote_topic_bible": "Библейские",
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
class ThemedQuote:
    topic: str
    text: str
    author: str
    translation: str | None = None


BASE_THEMED_QUOTES: dict[str, dict[str, list[ThemedQuote]]] = {
    "ru": {
        "family": [
            ThemedQuote("family", "Все счастливые семьи похожи друг на друга.", "Лев Толстой"),
            ThemedQuote("family", "Семья - один из шедевров природы.", "Джордж Сантаяна"),
            ThemedQuote("family", "Если хотите изменить мир, идите домой и любите свою семью.", "Мать Тереза"),
            ThemedQuote("family", "Единственная скала, которая не подводит, - семья.", "Ли Якокка"),
            ThemedQuote("family", "Семья - самое важное в мире.", "Принцесса Диана"),
        ],
        "discipline": [
            ThemedQuote("discipline", "Мы есть то, что постоянно делаем.", "Аристотель"),
            ThemedQuote("discipline", "Дисциплина - мост между целями и достижениями.", "Джим Рон"),
            ThemedQuote("discipline", "Дисциплина равна свободе.", "Джоко Виллинк"),
            ThemedQuote("discipline", "Я не боюсь того, кто тренирует 10 000 ударов однажды.", "Брюс Ли"),
            ThemedQuote("discipline", "Никто не свободен, кто не владеет собой.", "Эпиктет"),
        ],
        "health": [
            ThemedQuote("health", "Пусть пища будет твоим лекарством.", "Гиппократ"),
            ThemedQuote("health", "Здоровье не все, но без здоровья все - ничто.", "Артур Шопенгауэр"),
            ThemedQuote("health", "У кого нет времени для здоровья, найдет время для болезни.", "Эдвард Стэнли"),
            ThemedQuote("health", "Физическая форма - первое условие счастья.", "Джозеф Пилатес"),
            ThemedQuote("health", "Величайшее богатство - здоровье.", "Вергилий"),
        ],
        "children": [
            ThemedQuote("children", "Лучший способ сделать детей хорошими - сделать их счастливыми.", "Оскар Уайльд"),
            ThemedQuote("children", "Детей нет - есть люди.", "Януш Корчак"),
            ThemedQuote("children", "Никогда не помогайте ребенку с задачей, которую он может решить сам.", "Мария Монтессори"),
            ThemedQuote("children", "О душе общества лучше всего говорит то, как оно относится к детям.", "Нельсон Мандела"),
            ThemedQuote("children", "Детям больше нужен пример, чем критика.", "Жозеф Жубер"),
        ],
        "leadership": [
            ThemedQuote("leadership", "Лидерство - это способность превращать видение в реальность.", "Уоррен Беннис"),
            ThemedQuote("leadership", "Лидер знает путь, идет этим путем и показывает путь.", "Джон Максвелл"),
            ThemedQuote("leadership", "Менеджмент - делать дела правильно, лидерство - делать правильные дела.", "Питер Друкер"),
            ThemedQuote("leadership", "Пример - не главный способ влиять на других, а единственный.", "Альберт Швейцер"),
            ThemedQuote("leadership", "Если ваши действия вдохновляют других мечтать больше, вы лидер.", "Джон Куинси Адамс"),
        ],
        "bible": [
            ThemedQuote(
                "bible",
                "Больше всего хранимого храни сердце твое, потому что из него источники жизни.",
                "Библия, Притчи 4:23",
            ),
            ThemedQuote(
                "bible",
                "Делая добро, да не унываем, ибо в свое время пожнем, если не ослабеем.",
                "Библия, Галатам 6:9",
            ),
            ThemedQuote(
                "bible",
                "Все могу в укрепляющем меня Иисусе Христе.",
                "Библия, Филиппийцам 4:13",
            ),
            ThemedQuote(
                "bible",
                "Так да светит свет ваш пред людьми, чтобы они видели ваши добрые дела и прославляли Отца вашего Небесного.",
                "Библия, Матфея 5:16",
            ),
            ThemedQuote(
                "bible",
                "А надеющиеся на Господа обновятся в силе: поднимут крылья, как орлы, потекут - и не устанут, пойдут - и не утомятся.",
                "Библия, Исаия 40:31",
            ),
            ThemedQuote(
                "bible",
                "Пусть любовь и верность никогда не покидают тебя; навяжи их на шею, запиши их на скрижали сердца.",
                "Библия, Притчи 3:3",
                translation="nrp",
            ),
            ThemedQuote(
                "bible",
                "Не заботьтесь ни о чем, но во всем, с молитвой и просьбой, с благодарностью открывайте свои желания Богу.",
                "Библия, Филиппийцам 4:6",
                translation="nrp",
            ),
            ThemedQuote(
                "bible",
                "Прежде всего ищите Царства Божьего и Его праведности, и все это вам тоже будет дано.",
                "Библия, Матфея 6:33",
                translation="nrp",
            ),
            ThemedQuote(
                "bible",
                "Будь тверд и мужественен! Не бойся и не ужасайся, потому что с тобой Господь, твой Бог, куда бы ты ни пошел.",
                "Библия, Иисуса Навина 1:9",
                translation="nrp",
            ),
            ThemedQuote(
                "bible",
                "Мы знаем, что Бог во всем действует во благо тех, кто любит Его, кто призван согласно Его замыслу.",
                "Библия, Римлянам 8:28",
                translation="nrp",
            ),
        ],
    },
    "en": {
        "family": [
            ThemedQuote("family", "All happy families are alike.", "Leo Tolstoy"),
            ThemedQuote("family", "The family is one of nature's masterpieces.", "George Santayana"),
            ThemedQuote("family", "If you want to change the world, go home and love your family.", "Mother Teresa"),
            ThemedQuote("family", "The only rock I know that stays steady is the family.", "Lee Iacocca"),
            ThemedQuote("family", "Family is the most important thing in the world.", "Princess Diana"),
        ],
        "discipline": [
            ThemedQuote("discipline", "We are what we repeatedly do.", "Aristotle"),
            ThemedQuote("discipline", "Discipline is the bridge between goals and accomplishment.", "Jim Rohn"),
            ThemedQuote("discipline", "Discipline equals freedom.", "Jocko Willink"),
            ThemedQuote("discipline", "I fear not the man who has practiced 10,000 kicks once.", "Bruce Lee"),
            ThemedQuote("discipline", "No man is free who is not master of himself.", "Epictetus"),
        ],
        "health": [
            ThemedQuote("health", "Let food be thy medicine.", "Hippocrates"),
            ThemedQuote("health", "Health is not everything, but without health everything is nothing.", "Arthur Schopenhauer"),
            ThemedQuote("health", "Those who think they have no time for health will sooner or later have to find time for illness.", "Edward Stanley"),
            ThemedQuote("health", "Physical fitness is the first requisite of happiness.", "Joseph Pilates"),
            ThemedQuote("health", "The greatest wealth is health.", "Virgil"),
        ],
        "children": [
            ThemedQuote("children", "The best way to make children good is to make them happy.", "Oscar Wilde"),
            ThemedQuote("children", "There are no children, there are people.", "Janusz Korczak"),
            ThemedQuote("children", "Never help a child with a task at which he feels he can succeed.", "Maria Montessori"),
            ThemedQuote("children", "There can be no keener revelation of a society's soul than the way it treats its children.", "Nelson Mandela"),
            ThemedQuote("children", "Children need models rather than critics.", "Joseph Joubert"),
        ],
        "leadership": [
            ThemedQuote("leadership", "Leadership is the capacity to translate vision into reality.", "Warren Bennis"),
            ThemedQuote("leadership", "A leader knows the way, goes the way, and shows the way.", "John C. Maxwell"),
            ThemedQuote("leadership", "Management is doing things right; leadership is doing the right things.", "Peter Drucker"),
            ThemedQuote("leadership", "Example is not the main thing in influencing others. It is the only thing.", "Albert Schweitzer"),
            ThemedQuote("leadership", "If your actions inspire others to dream more, you are a leader.", "John Quincy Adams"),
        ],
        "bible": [
            ThemedQuote("bible", "Above all else, guard your heart.", "Bible, Proverbs 4:23"),
            ThemedQuote("bible", "Let us not become weary in doing good.", "Bible, Galatians 6:9"),
            ThemedQuote("bible", "I can do all things through Christ who strengthens me.", "Bible, Philippians 4:13"),
            ThemedQuote("bible", "Let your light shine before others.", "Bible, Matthew 5:16"),
            ThemedQuote("bible", "Those who hope in the Lord will renew their strength.", "Bible, Isaiah 40:31"),
        ],
    },
}

THEMED_QUOTES: dict[str, dict[str, list[ThemedQuote]]] = BASE_THEMED_QUOTES


def random_thematic_quote(lang: str, previous: ThemedQuote | None = None) -> ThemedQuote:
    lang_key = "en" if lang == "en" else "ru"
    pool = [quote for topic_quotes in THEMED_QUOTES[lang_key].values() for quote in topic_quotes]
    if previous is not None:
        filtered = [quote for quote in pool if quote != previous]
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
