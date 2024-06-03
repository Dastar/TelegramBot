import re


class AIMessage:
    def __init__(self, role:str, content:str):
        self.role = role
        self.content = content
        # self.tags = re.findall(r'%%.*?%%', content)

    def format_content(self, tag, text):
        return self.content.replace(tag, text)

    def create_message(self, text):
        content = self.format_content('%%TEXT%%', text)
        return {"role": self.role, "content": content}

