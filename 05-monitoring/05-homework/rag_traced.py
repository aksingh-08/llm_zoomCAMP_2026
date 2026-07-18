import time
from rag_helper import RAGBase
from opentelemetry import trace
tracer = trace.get_tracer("llm-zoomcamp")

class RAGTraced(RAGBase):
    def search(self, query, num_results=5):
        with tracer.start_as_current_span("search"):
            start = time.perf_counter()
            result = super().search(query, num_results)
            print(f'Search took {(time.perf_counter() - start) * 1000:.2f} ms')
            return result
            # return super().search(query, num_results)

    def llm(self, prompt):
        with tracer.start_as_current_span("llm") as span:
            start = time.perf_counter()
            
            input_messages = [
                {'role': 'developer', 'content': self.instructions},
                {'role': 'user', 'content': prompt},
            ]
            response = self.llm_client.beta.chat.completions.create(
                model=self.model,
                messages=input_messages,
            )
            duration = time.perf_counter() - start
            print(f'LLM took {duration:.3f} seconds')
            # return super().llm(prompt)
            usage = response.usage
            span.set_attribute('duration_seconds', duration)
            span.set_attribute('model', self.model)
            span.set_attribute('input_tokens', usage.prompt_tokens)
            span.set_attribute('output_tokens', usage.completion_tokens)
            span.set_attribute('total_tokens', usage.total_tokens)

            input_price_per_million = 0.75
            output_price_per_million = 4.5

            cost = (
                usage.prompt_tokens * input_price_per_million
                + usage.completion_tokens * output_price_per_million
            ) / 1_000_000

            span.set_attribute('cost', cost)
            return response

    def rag(self, query):
        with tracer.start_as_current_span("rag"):
            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            response = self.llm(prompt)
            return response.choices[0].message.content
            # return super().rag(query)