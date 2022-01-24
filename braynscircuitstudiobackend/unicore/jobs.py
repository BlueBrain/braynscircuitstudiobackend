class UnicoreJob:
    def __init__(self, job_id):
        self.job_id = job_id

    def start(self):
        raise NotImplementedError

    def upload_file(self):
        raise NotImplementedError
