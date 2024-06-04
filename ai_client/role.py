import re

from ai_client.ai_message import AIMessage


class Role:
    def __init__(self, name, system, user):
        self.name = name
        self.system = AIMessage("system", system)
        self.user = AIMessage("user", user)

    def init_tags(self, tags):
        for tag, element in tags.items():
            if not tag.startswith('%%'):
                tag = f'%%{tag}%%'
            self.user.replace_content(tag, element)

    def create_message(self, text):
        self.user.clear()
        self.user.format_content('%%TEXT%%', text)

        system = self.system.create_message()
        user = self.user.create_message()

        return [system, user]
