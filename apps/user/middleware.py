import json
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback


class ErrorMiddleware(BaseHTTPMiddleware):
    """
    Middlewar to catch unhandleed exceptions
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "details": traceback.format_exc(),
                    }
                },
            )


def http_exception_handler(request: Request, exc):
    """
    Function to handle http exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status": exc.status_code,
                "type": "HTTPException",
                "message": exc.detail,
            }
        },
    )


class ResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            if isinstance(response, JSONResponse):
                response_body = await response.body()  
                try:
                    response_data = json.loads(response_body.decode("utf-8"))  
                except json.JSONDecodeError:
                    response_data = None  

                formatted_response = {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "data": response_data,  
                    "message": "Request processed successfully",
                }
                return JSONResponse(content=formatted_response, status_code=response.status_code)

            return response
        except Exception as e:
            error_response = {
                "success": False,
                "status_code": 500,
                "data": None,
                "message": f"Internal Server Error: {str(e)}",
            }
            return JSONResponse(content=error_response, status_code=500)
