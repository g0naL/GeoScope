class ConflictEntity:
    def __init__(self, title, lat, language, description, url=None, polygon=None):
        self.title = title
        self.lat = lat
        self.language = language
        self.description = description
        self.url = url
        self.polygon = polygon or []
        self.conversations = []

    def add_conversation(self, conversation):
        self.conversations.append(conversation)

    def to_dict(self):
        return {
            "title": self.title,
            "lat": self.lat,
            "lng": self.lng,
            "description": self.description,
            "url": self.url,
            "polygon": self.polygon,
            "conversations": [c.to_dict() for c in self.conversations]
        }
