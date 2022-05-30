class Gang:
    def __init__(self, name: str):
        self.name = name
        self.lessons = []

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def __repr__(self):
        return self.name