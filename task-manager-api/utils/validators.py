import re
from datetime import datetime

from errors import AppError


VALID_STATUSES = ('pending', 'in_progress', 'done', 'cancelled')
VALID_ROLES = ('user', 'admin', 'manager')


def require_json(data):
    if not isinstance(data, dict) or not data:
        raise AppError('Dados inválidos')
    return data


def require_string(data, field, message, min_length=None, max_length=None):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise AppError(message)
    if min_length is not None and len(value) < min_length:
        raise AppError('Título muito curto' if field == 'title' else message)
    if max_length is not None and len(value) > max_length:
        raise AppError('Título muito longo' if field == 'title' else message)
    return value


def parse_integer(value, message, minimum=None, maximum=None):
    if isinstance(value, bool):
        raise AppError(message)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        raise AppError(message) from None
    if minimum is not None and parsed < minimum:
        raise AppError(message)
    if maximum is not None and parsed > maximum:
        raise AppError(message)
    return parsed


def validate_email(email):
    if not isinstance(email, str) or not re.fullmatch(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+', email):
        raise AppError('Email inválido')
    return email


def parse_date(value, message='Formato de data inválido'):
    if not value:
        return None
    if not isinstance(value, str):
        raise AppError(message)
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except ValueError:
        raise AppError(message) from None


def validate_task_fields(data, creating=False):
    require_json(data)
    result = {}
    if creating or 'title' in data:
        result['title'] = require_string(data, 'title', 'Título é obrigatório', 3, 200)
    for field in ('description',):
        if field in data:
            if data[field] is not None and not isinstance(data[field], str):
                raise AppError('Dados inválidos')
            result[field] = data[field]
    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise AppError('Status inválido')
        result['status'] = data['status']
    if 'priority' in data:
        result['priority'] = parse_integer(data['priority'], 'Prioridade deve ser entre 1 e 5', 1, 5)
    for field in ('user_id', 'category_id'):
        if field in data:
            result[field] = None if data[field] in (None, '') else parse_integer(data[field], 'Dados inválidos', 1)
    if 'due_date' in data:
        result['due_date'] = parse_date(data['due_date'])
    if 'tags' in data:
        tags = data['tags']
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            result['tags'] = ','.join(tags)
        elif isinstance(tags, str) or tags is None:
            result['tags'] = tags
        else:
            raise AppError('Dados inválidos')
    return result
