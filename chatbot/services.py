from rag.pipeline import RAGPipeline


class ChatService:

    def __init__(self):

        self.pipeline = RAGPipeline()


    def ask(self, question):

        response = self.pipeline.ask(
            question
        )

        return response