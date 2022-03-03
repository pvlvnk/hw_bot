class InvalidResponseError(Exception):
    """Проверяет запрос к эндпоинту."""

    pass


class InvalidTokenError(Exception):
    """Проверяет доступность токенов."""

    pass


class Error500Error(Exception):
    """Проверяет доступность эндпоинта."""

    pass


class NotContainHomeworksError(Exception):
    """Проверяет наличие новых статусов."""

    pass


class UnknownStatusError(Exception):
    """Проверяет валидность статуса."""

    pass


class HomeworkNameError(Exception):
    """Проверяет наличие имени у домашней работы."""

    pass


class ResponseNoHomeworksError(Exception):
    """Проверяет наличие ключа homeworks."""

    pass


class ResponseHomeworksNotInListError(Exception):
    """Проверяет, что под ключом homeworks пришел список."""

    pass


class ErrorNot200Error(Exception):
    """Проверяет доступность к эндпоинту."""

    pass
