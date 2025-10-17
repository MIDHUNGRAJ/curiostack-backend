import logging

# Configure the basic logging settings
# This sets the logging level to INFO, meaning messages at INFO, WARNING, ERROR, and CRITICAL levels will be processed.
# It also defines a format for the log messages.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Log messages at different severity levels
logging.debug("This is a debug message.")  # This message will not be shown due to the INFO level setting.
logging.info("This is an informational message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
logging.critical("This is a critical message.")

def divide_numbers(a, b):
    try:
        result = a / b
        logging.info(f"Division successful: {a} / {b} = {result}")
        return result
    except ZeroDivisionError:
        logging.error("Attempted to divide by zero!")
        return None

divide_numbers(10, 2)
divide_numbers(5, 0)
