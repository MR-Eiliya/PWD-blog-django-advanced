import threading


class EmailThread(threading.Thread):
    def __init__(self, email_obj):
        super().__init__(group=None)
        self.email_obj = email_obj

    def run(self):
        self.email_obj.send()
