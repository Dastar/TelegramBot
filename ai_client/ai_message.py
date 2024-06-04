import re


class AIMessage:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.edited_content = ''
        # self.tags = re.findall(r'%%.*?%%', content)

    def clear(self):
        self.edited_content = ''

    def _format_content(self, tag, text):
        return self.content.replace(tag, text)

    def replace_content(self, tag, text):
        self.content = self._format_content(tag, text)

    def format_content(self, tag, text):
        self.edited_content = self._format_content(tag, text)

    def create_message(self, text=''):
        if self.edited_content.strip():
            content = self.edited_content
        else:
            content = self._format_content('%%TEXT%%', text)
        return {"role": self.role, "content": content}

