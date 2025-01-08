class InMemoryStorage:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key, None)

    def display_all(self):
        print("Wszystkie dane:")
        for key, value in self.data.items():
            print(f"{key}: {value}")



memory_storage = InMemoryStorage()