import csv
import io
from typing import List
from datetime import datetime

from database.models import Tasks
from common.utils import get_priority_text
from common.logger import get_logger

logger = get_logger(__name__)


def get_status_text(status: int) -> str:
    """Получить текстовое представление статуса"""
    return "Выполнена" if status == 1 else "Активна"


def format_deadline(deadline) -> str:
    """Форматировать дедлайн для CSV"""
    if not deadline:
        return "Не установлен"

    try:
        # Если это объект datetime
        if hasattr(deadline, 'strftime'):
            return deadline.strftime('%d.%m.%Y %H:%M')
        # Если deadline это строка с датой и временем
        elif isinstance(deadline, str):
            # Пробуем разные форматы
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                try:
                    dt = datetime.strptime(deadline, fmt)
                    return dt.strftime('%d.%m.%Y %H:%M')
                except ValueError:
                    continue

        return str(deadline)
    except Exception:
        return str(deadline) if deadline else "Не установлен"


def format_datetime(dt: datetime) -> str:
    """Форматировать datetime для CSV"""
    if not dt:
        return ""
    return dt.strftime('%d.%m.%Y %H:%M')


from typing import List

async def generate_csv_content(tasks: List["Tasks"]) -> str:
    output = io.StringIO(newline="")  # корректно работает с csv.writer
    # Первая строка — подсказка Excel о разделителе и одновременно увод от "ID" в начале файла
    output.write("sep=;\r\n")

    fieldnames = [
        "ID",
        "Текст задачи",
        "Дедлайн",
        "Приоритет",
        "Статус",
        "Дата создания",
        "Дата обновления",
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=";",
        lineterminator="\r\n",
    )

    writer.writeheader()

    for task in tasks:
        try:
            writer.writerow({
                "ID": task.id,
                "Текст задачи": task.text,
                "Дедлайн": format_deadline(task.deadline),
                "Приоритет": get_priority_text(task.priority),
                "Статус": get_status_text(task.status),
                "Дата создания": format_datetime(task.created_at),
                "Дата обновления": format_datetime(task.updated_at),
            })
        except Exception as e:
            writer.writerow({
                "ID": getattr(task, "id", "N/A"),
                "Текст задачи": getattr(task, "text", "Ошибка загрузки"),
                "Дедлайн": "Ошибка",
                "Приоритет": "Ошибка",
                "Статус": "Ошибка",
                "Дата создания": "Ошибка",
                "Дата обновления": f"Ошибка: {str(e)}",
            })

    return output.getvalue()


def generate_filename(user_id: int) -> str:
    """Генерировать имя файла для экспорта"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"tasks_export_{user_id}_{timestamp}.csv"
