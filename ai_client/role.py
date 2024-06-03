import re

from ai_client.ai_message import AIMessage


class Role:
    def __init__(self, system, user):
        self.system = AIMessage("system", system)
        self.user = AIMessage("user", user)
        self.tags = re.findall(r'%%.*?%%', user)

    def create_message(self, tags, texts):
        self.user.clear()
        for tag, text in zip(tags, texts):
            self.user.format_content(tag, text)

        system = self.system.create_message()
        user = self.user.create_message()

        return [system, user]
