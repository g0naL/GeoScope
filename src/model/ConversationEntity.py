class ConversationEntity:
    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.comments = []

    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "comments": self.comments
        }
