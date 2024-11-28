import openai
import torch
from transformers import AutoTokenizer, AutoModel

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

def average_eval_results(eval_results):
    if not eval_results:
        return None

    total_scores = {
        "overall_score": 0,
        "grammar_score": 0,
        "logic_score": 0,
        "relevance_score": 0
    }
    count = len(eval_results)

    for result in eval_results:
        total_scores["overall_score"] += result.overall_score
        total_scores["grammar_score"] += result.grammar_score
        total_scores["logic_score"] += result.logic_score
        total_scores["relevance_score"] += result.relevance_score

    average_scores = {key: value / count for key, value in total_scores.items()}
    return EvalResult(average_scores)
    
class QustionList:
    def __init__(self, data_dict=None):
        if data_dict is None:
            data_dict = {}
        self.questions = data_dict.get("questions", [])
    
    def to_dict(self):
        return {
            "questions": self.questions
        }
    
    def getQuestions(self):
        return self.questions
    
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

    def evaluate(self, query, answer):
        prompt = f"Evaluate this answer to question, give overall_score,grammar_score, logic_score, relevance_score with rationale, from scale 1-10, 10 indicate the best, Question: {query}\nAnswer: {answer}\n}\n"
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
    def __init__(self, model_name="gpt-4o-2024-08-06"):
        self.client =  openai.OpenAI();
        self.model_name = model_name

    def generate_questions(self, text):
        prompt = f"Text: {text}\nGenerate 3 questions can be answered by the text. Assume whoever answers don't have access to the text, so you should give some context but don't refer to the text, never mention 'according to this text, or the function, the class' etc, use the full name instead if you want to refer to text\n"
        response = self.client.chat.completions.create(
            model=self.model_name,
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

def calculate_embedding_similarity(text1, text2):
    """
    Calculates the cosine similarity between the embeddings of two input texts.

    Args:
        text1 (str): The first input text.
        text2 (str): The second input text.

    Returns:
        float: The cosine similarity between the embeddings of the two input texts.
    """
    # Get the embeddings for the input texts
    embedding1 = get_sentence_embedding(text1)
    embedding2 = get_sentence_embedding(text2)
    # Calculate the cosine similarity between the embeddings
    similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2, dim=0).item()
    return similarity

def get_sentence_embedding(sentence):
    model_name = "sentence-transformers/all-MiniLM-L6-v2"  # A model suitable for sentence embeddings
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    # Tokenize input and get model output
    inputs = tokenizer(sentence, return_tensors="pt")
    outputs = model(**inputs)
    # Mean pool the token embeddings to get the sentence embedding
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embedding

def main():
    # Test the function
    text1 = "I like cats"
    text2 = "I love dogs"
    similarity = calculate_embedding_similarity(text1, text2)
    print(f"Embedding Similarity: {similarity}")


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