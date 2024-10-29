import openai

class EvalResult:
    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = {}
        self.overall_score = data_dict.get("overall_score", None)
        self.overall_rationale = data_dict.get("overall_rationale", None)
        self.grammar_score = data_dict.get("grammar_score", None)
        self.grammar_rationale = data_dict.get("grammar_rationale", None)
        self.logic_score = data_dict.get("logic_score", None)
        self.logic_rationale = data_dict.get("logic_rationale", None)
        self.relevance_score = data_dict.get("relevance_score", None)
        self.relevance_rationale = data_dict.get("relevance_rationale", None)

    def to_dict(self):
        return {
            "overall_score": self.overall_score,
            "overall_rationale": self.overall_rationale,
            "grammar_score": self.grammar_score,
            "grammar_rationale": self.grammar_rationale,
            "logic_score": self.logic_score,
            "logic_rationale": self.logic_rationale,
            "relevance_score": self.relevance_score,
            "relevance_rationale": self.relevance_rationale
        }
    
    @staticmethod
    def to_json_schema():
        return {
            "type": "object",
            "properties": {
                "overall_score": {"type": "number"},
                "overall_rationale": {"type": "string"},
                "grammar_score": {"type": "number"},
                "grammar_rationale": {"type": "string"},
                "logic_score": {"type": "number"},
                "logic_rationale": {"type": "string"},
                "relevance_score": {"type": "number"},
                "relevance_rationale": {"type": "string"}
            },
            "required": ["overall_score", "overall_rationale", "grammar_score", "grammar_rationale", "logic_score", "logic_rationale", "relevance_score", "relevance_rationale"],
            "additionalProperties": False,
        }
    
    
class QustionList:
    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = {}
        self.questions = data_dict.get("questions", [])
    
    def to_dict(self):
        return {
            "questions": self.questions
        }
    
    @staticmethod
    def to_json_schema():
        return {
            "type": "object",
            "properties": {
                "questions": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["questions"],
            "additionalProperties": False,
        }
    
    

class DirectLLMEvalWithOpenAI:
    def __init__(self):
        self.client = openai.OpenAI();

    def evaluate(self, query, context):
        prompt = f"Query: {query}\nContext: {context}\nReturn JSON: {EvalResult().to_dict()}\n"
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format = {
                "type": "json_schema",
                "json_schema":
                 {
                    "schema": EvalResult.to_json_schema(),
                    "name": "EvalResult",
                    "strict": True
                 } 
                
            }
        )
        generated_text = response.choices[0].message.content.strip()
        try:
            data_dict = eval(generated_text)
            eval_result = EvalResult(data_dict)
        except Exception as e:
            print(f"Error: {e}")
            eval_result = None
        return eval_result
    
class GenerateQuestionsBasedOnText:
    def __init__(self):
        self.client =  openai.OpenAI();

    def generate_questions(self, text):
        prompt = f"Text: {text}\nGenerate questions can be answered by the text.\n"
        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            response_format = {
                "type": "json_schema",
                "json_schema":   {
                    "schema": QustionList.to_json_schema(),
                    "name": "QustionList",
                    "strict": True
                 } 
                
            }
        )
        generated_text =  response.choices[0].message.content.strip()
        try:
            data_dict = eval(generated_text)
            questions = data_dict.get("questions", [])
        except Exception as e:
            print(f"Error: {e}")
            questions = []
        return questions


def main():
    # Create instances of the classes
    eval_api = DirectLLMEvalWithOpenAI()
    generate_api = GenerateQuestionsBasedOnText()

    # Test the evaluation API
    query = "What is the capital of France?"
    context = "France is a country located in Western Europe."
    eval_result = eval_api.evaluate(query, context)
    print("Evaluation Result:")
    print(eval_result.to_dict())

    # Test the question generation API
    text = "The Mona Lisa is a famous painting created by Leonardo da Vinci."
    questions = generate_api.generate_questions(text)
    print("Generated Questions:")
    for question in questions:
        print(question)

if __name__ == "__main__":
    main()