import time
from threading import Thread
import core.leagues
from match_process import Process


class QueueUrl(Thread):
    def __init__(self):
        super(QueueUrl, self).__init__()
        self.queue = []
        self.today = None
        self.is_parsed = False
        self.is_working = False
        self.number_of_history_matches = 5

    def queue_append(self, value):
        if value not in self.queue:
            self.queue.append(value)

    def queue_append_array(self, value):
        for key in value:
            self.queue_append(key)

    def queue_get(self):
        return self.queue.pop()

    def queue_last_parsed(self, today):
        self.today = today

    def queue_status(self, is_parsed):
        self.is_parsed = is_parsed

    def print_queue(self):
        if self.is_working is False:
            print('-----------------------------------------------')
            print('Сегодня:', time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
            print('Размер очереди:', len(self.queue))
            print('Статус:', self.is_parsed)
            print('Дата последнего обновления:', time.strftime("%a, %d %b %Y %H:%M:%S", self.today))
            print('-----------------------------------------------')
        else:
            pass

    def run(self):
        self.today = time.localtime()
        while True:
            if len(self.queue) != 0:
                self.is_working = True
                process = Process(self.number_of_history_matches, self.queue_get())
                process.start()
                process.join()
                self.is_working = False
                time.sleep(2)
                self.print_queue()
            else:
                time.sleep(2)


def main():
    queue_url = QueueUrl()
    queue_url.start()
    queue_url.print_queue()
    while True:
        if time.localtime()[2] != queue_url.today[2] or queue_url.is_parsed is False:
            sports = core.leagues.start()
            for sport in sports:
                if len(sport.leagues) != 0:
                    for league in sport.leagues:
                        queue_url.queue_append_array(league.matches_urls)
            queue_url.queue_status(True)
            queue_url.queue_last_parsed(time.localtime())
        else:
            if queue_url.is_working is False:
                print("Server is waiting for new queue!")
                queue_url.print_queue()
                time.sleep(60)
            else:
                time.sleep(60)


if __name__ == "__main__":
    main()
