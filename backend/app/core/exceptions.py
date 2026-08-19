from typing import Any


class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(code="NOT_FOUND", message=message, status_code=404)


class ConflictError(AppError):
    def __init__(
        self,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            status_code=409,
            details=details,
        )


class ValidationAppError(AppError):
    def __init__(
        self,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(code="UNAUTHORIZED", message=message, status_code=401)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Not allowed in this environment") -> None:
        super().__init__(code="FORBIDDEN", message=message, status_code=403)
