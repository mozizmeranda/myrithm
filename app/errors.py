from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def create_error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message
            }
        }
    )

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return create_error_response(exc.code, exc.message, exc.status_code)

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # Map status code to standard string code if needed
    code_map = {
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    code = code_map.get(exc.status_code, "ERROR")
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail:
        code = detail.get("code", code)
        message = detail.get("message", str(detail))
    elif isinstance(detail, str):
        message = detail
    else:
        message = str(detail)
    return create_error_response(code, message, exc.status_code)

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    msg = first_error.get("msg", "Validation error")
    loc = ".".join([str(l) for l in first_error.get("loc", []) if l != "body"])
    full_msg = f"{loc}: {msg}" if loc else msg
    return create_error_response("VALIDATION_ERROR", full_msg, status.HTTP_422_UNPROCESSABLE_ENTITY)

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)
