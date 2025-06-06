from fastapi import Request  # Import the Request object to access request data
import logging  # Python's built-in logging module
import time  # Used to calculate how long the request took

# Configure the logging level to INFO so that log messages of level INFO and above will be printed
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Create a logger for this file/module

# This function is a custom middleware to log how long each request takes
async def logging_middleware(request: Request, call_next):
    start_time = time.time()  # Record the time just before processing the request

    response = await call_next(request)  # Pass the request to the next handler and wait for response

    process_time = time.time() - start_time  # Calculate how long the request took

    # Log the method (e.g., GET, POST), the path (e.g., /api/items), and the time taken
    logger.info(f"{request.method} {request.url.path} - Completed in {process_time:.2f}s")

    return response  # Return the response to the client
