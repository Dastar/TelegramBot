from datetime import datetime


class Helpers:
    @staticmethod
    def extract_code_blocks(text):
        """Extract code blocks from the text."""
        import re
        code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
        code_blocks = code_block_pattern.findall(text)
        for i, block in enumerate(code_blocks):
            text = text.replace(block, f"[CODE_BLOCK_{i}]")
        return text, code_blocks

    @staticmethod
    def insert_code_blocks(text, code_blocks):
        """Insert code blocks back into the translated text."""
        for i, block in enumerate(code_blocks):
            text = text.replace(f"[CODE_BLOCK_{i}]", block)
        return text

    @staticmethod
    def first_non_alpha(text: str):
        i = 0
        while text[i].isalpha():
            i += 1
        return i

    @staticmethod
    def time_to_timestamp(time_str):
        # Define the format of the input time string
        time_format = "%H:%M"
        # Convert the time string to a datetime object
        time_obj = datetime.strptime(time_str, time_format)
        # Convert the datetime object to a timestamp
        timestamp = time_obj.timestamp()
        return timestamp

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False
