class QueueItem:

    def __init__(self, q_item, q):
        self.id = q_item['id']
        self.data = q_item['data']
        self.q = q

    def complete(self):
        self.q.complete(self.id)

    def fail(self):
        self.q.fail(self.id)
