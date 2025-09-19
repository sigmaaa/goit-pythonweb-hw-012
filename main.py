"""
Main FastAPI application entry point.

This module initializes the FastAPI app, configures middleware,
rate limiting, and includes all API routers.

Routers included:
    - utils (general utility routes)
    - contacts (contact management)
    - auth (authentication and authorization)
    - users (user management)

It also sets up:
    - CORS middleware for frontend communication
    - Request rate limiting using `slowapi`
    - Exception handler for rate limit errors

To run locally:
    $ uvicorn main:app --reload
"""

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from src.api import utils, contacts, auth, users
from fastapi.middleware.cors import CORSMiddleware

# Initialize Limiter
limiter = Limiter(key_func=lambda request: request.client.host)

#: Main FastAPI application instance.
app = FastAPI()

#: Allowed origins for CORS.
origins = ["http://localhost:3000"]

# Attach middleware
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handle `RateLimitExceeded` exceptions.

    This function intercepts requests that exceed the configured
    rate limit and returns a JSON response with HTTP 429.

    :param request: The incoming request object.
    :type request: Request
    :param exc: The exception instance raised by slowapi.
    :type exc: RateLimitExceeded
    :return: JSON response with error message.
    :rtype: JSONResponse
    """
    return JSONResponse(
        status_code=429,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


if __name__ == "__main__":
    import uvicorn

    #: Run the FastAPI application with autoreload enabled.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
