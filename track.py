class Track:
    def __init__(self, title: str, start: int, duration: int) -> None:
        self.title = title
        self.start = start
        self.duration = duration

    def __str__(self) -> str:
        return f"{self.title} ({self.start} - {self.duration})"
    
    def __repr__(self):
        return str(self)