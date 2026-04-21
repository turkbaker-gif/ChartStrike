from app.workers.itick_refresh_worker import ITickRefreshWorker

if __name__ == "__main__":
    ITickRefreshWorker.run_forever()