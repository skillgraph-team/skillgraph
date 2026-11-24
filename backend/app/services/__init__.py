"""Services: the business logic that reads and writes the database.

Services raise domain exceptions (e.g. `EmailTakenError`); only `app/api` turns them
into HTTP errors. Services flush; the endpoint commits.
"""
