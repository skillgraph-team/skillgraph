"""HTTP endpoints (FastAPI routers). One module per area; each is registered in app/main.py.

Endpoints validate input, check who is calling (`CurrentUser`), call a service, commit,
and turn domain exceptions into HTTP errors. Errors are codes, never sentences:
`{"detail": {"code": "email_taken"}}`; the frontend translates them.
"""
