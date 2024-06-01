import ai_client
import simple_client
from tasks.task import Task


class MessageGenerator(Task):
    def __init__(self, ai: ai_client.AIClient, targets):
        self.ai_client = ai
        self.targets = targets

    def create_role(self):
        self.ai_client.add_role("system", content="You are a software engineer and blogger")
        self.ai_client.add_role("user",
                                content="This GPT is a software engineer and a blogger. This GPT knows everything "
                                        "about writing good and trusted software. This GPT is writing a blog about "
                                        "algorithms. This GPT will write a post in his blog about little known "
                                        "algorithms, each time only one, no more than 40 lines of code. It will give "
                                        "little explanation about the generated code. The explanations should be "
                                        "for people with some experience in programming. The GPT will choose "
                                        "itself the algorithm. The GPT will only response "
                                        "with the code and explanations, nothing else should be in the response. "
                                        "Output only the actual answer.")

    async def run(self, client):
        message = await self.ai_client.run_model("")
        if message:
            for target in self.targets:
                await client.send(target, message)






