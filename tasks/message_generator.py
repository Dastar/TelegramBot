import ai_client
import simple_client
from tasks.task import Task


class MessageGenerator(Task):
    def __init__(self, delay, ai: ai_client.AIClient, tg_client: simple_client.SimpleClient, targets):
        super().__init__(delay)
        self.ai_client = ai
        self.tg_client = tg_client
        self.targets = targets

    def create_role(self):
        self.ai_client.add_role("system", content="You are a speech motivator")
        self.ai_client.add_role("user", content="This GPT is a speech motivator, knows a little about a log of thinks and can speak about everything."
                                                "The GPT will generate a small speech about 300 character about some of the things it thinks interesting right now."
                                                "The GPT will respond only with the speech, nothing else should be in the responde.")

    async def run(self):
        if not await super().run():
            return False

        message = await self.ai_client.run_model("")
        if message:
            for target in self.targets:
                await self.tg_client.send(target, message)

        return True





