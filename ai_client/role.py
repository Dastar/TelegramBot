import re

from ai_client.ai_message import AIMessage


class Role:
    def __init__(self, name, system, user):
        self.name = name
        self.system = AIMessage("system", system)
        self.user = AIMessage("user", user)
        self.tags = None

    def init_tags(self, tags=None):
        if tags is not None:
            self.tags = tags
        for tag, element in self.tags.items():
            if not tag.startswith('%%'):
                tag = f'%%{tag}%%'
            self.user.replace_content(tag, element)

    def create_message(self, text):
        self.user.clear()
        self.user.format_content('%%TEXT%%', text)

        system = self.system.create_message()
        user = self.user.create_message()

        return [system, user]

    def __str__(self):
        return f'/role : {self.name}\n===\nname: {self.name}\n===\n{self.system}\n===\n{self.user}'

    def from_text(self, text: str):
        lines = text.split('===')
        lines = [line.split(':', maxsplit=1) for line in lines]
        d = {key.strip(): value.strip() for key, value in lines}
        self.system = AIMessage('system', d['system'])
        self.user = AIMessage('user', d['user'])
        self.init_tags()
