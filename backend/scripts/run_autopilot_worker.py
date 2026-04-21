from app.workers.autopilot_worker import AutopilotWorker


if __name__ == "__main__":
    worker = AutopilotWorker()
    worker.run_forever()