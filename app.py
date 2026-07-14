import logging
import os
import random
import time
from logging.handlers import RotatingFileHandler

import psutil
from flask import Flask, jsonify, g, request


LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

app = Flask(__name__)


class RequestContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        defaults = {
            "endpoint": "-",
            "method": "-",
            "status": "-",
            "duration_ms": "-",
        }
        for key, value in defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        return True


def configure_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s endpoint=%(endpoint)s method=%(method)s "
        "status=%(status)s duration_ms=%(duration_ms)s message=%(message)s"
    )

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(RequestContextFilter())

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(RequestContextFilter())

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.handlers.clear()
    werkzeug_logger.propagate = False


def log_event(level: int, message: str, status: int = 200, duration_ms: int = 0) -> None:
    logging.log(
        level,
        message,
        extra={
            "endpoint": request.path if request else "-",
            "method": request.method if request else "-",
            "status": status,
            "duration_ms": duration_ms,
        },
    )


@app.before_request
def start_timer() -> None:
    g.start_time = time.perf_counter()


@app.after_request
def log_request(response):
    duration_ms = int((time.perf_counter() - g.start_time) * 1000)
    if request.path not in {"/favicon.ico"}:
        log_event(
            logging.INFO,
            "request_completed",
            status=response.status_code,
            duration_ms=duration_ms,
        )
    return response


@app.route("/")
def home():
    return jsonify(
        application="splunk-datadog-demo",
        status="running",
        endpoints=["/", "/login", "/health", "/error", "/slow", "/cpu", "/metrics"],
    )


@app.route("/login")
def login():
    user = random.choice(["admin", "john", "alice", "devops"])
    log_event(logging.INFO, f"login_success user={user}")
    return jsonify(message="Login successful", user=user)


@app.route("/health")
def health():
    log_event(logging.INFO, "health_check_ok")
    return jsonify(status="healthy")


@app.route("/error")
def error():
    try:
        _ = 10 / 0
    except ZeroDivisionError as exc:
        log_event(logging.ERROR, f"simulated_error error={exc}", status=500)
    return jsonify(message="Error logged"), 500


@app.route("/slow")
def slow():
    delay = random.uniform(2.0, 4.0)
    time.sleep(delay)
    log_event(logging.WARNING, f"slow_response delay_seconds={delay:.2f}")
    return jsonify(message="Slow response generated", delay_seconds=round(delay, 2))


@app.route("/cpu")
def cpu():
    limit = int(request.args.get("limit", "12000000"))
    total = 0
    for value in range(limit):
        total += value * value
    log_event(logging.INFO, f"cpu_load_generated iterations={limit}")
    return jsonify(message="CPU load generated", iterations=limit, result=total)


@app.route("/metrics")
def metrics():
    snapshot = {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
    }
    log_event(logging.INFO, f"metrics_snapshot values={snapshot}")
    return jsonify(snapshot)


configure_logging()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
