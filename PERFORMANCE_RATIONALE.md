# Performance Optimization Rationale: Synchronous DB I/O in Async Endpoints

## Issue
The FastAPI application uses synchronous SQLAlchemy for database operations. Several endpoints in `app/routers/auth.py` and dependencies in `app/dependencies.py` are defined as `async def` but perform these synchronous, blocking DB operations.

In FastAPI, `async def` functions run directly on the main event loop. If they perform blocking I/O (like synchronous DB queries), they block the entire event loop, preventing other concurrent requests from being handled until the I/O operation completes.

## Optimization
By converting these functions from `async def` to regular `def`, FastAPI will automatically run them in a separate thread pool. This allows the main event loop to continue handling other requests while the blocking I/O is being performed in a background thread, significantly improving the application's concurrency and throughput.

## Baseline and Measurement
Measurement in the current environment was impractical because:
1. Necessary dependencies (`fastapi`, `sqlalchemy`, etc.) were not installed in the available Python environments.
2. Network access was restricted, preventing the installation of these dependencies.
3. No existing benchmarks or load testing tools were available in the codebase.

## Technical Rationale
According to [FastAPI documentation](https://fastapi.tiangolo.com/async/#path-operation-functions):
> "When you declare a path operation function with normal `def` instead of `async def`, it is run in an external threadpool that is then awaited, instead of being called directly (as it would block the loop)."

Since the codebase uses synchronous SQLAlchemy, using `def` for these endpoints is the recommended best practice for performance and scalability.
