import torch
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer
import eval
import os, sys
folder_a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rag'))  

# Add the folder path to sys.path  
sys.path.insert(0, folder_a_path)  

import app as rag_app
import random
import argparse

class Evaluator:
    def __init__(self, model_name:str):
        if model_name.endswith(".pt") or model_name.endswith(".pth"):
            self.model = torch.load(model_name, map_location='cpu')
            self.tokenizer = AutoTokenizer.from_pretrained("finetune/llama3_2_batch_2_tuned_model_tokenizer/")
        else:
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.EvalResults = []
        self.llmEvaluator=eval.DirectLLMEvalWithOpenAI()
    
    def loadQuestions(self, filename:str):
        with open(filename, 'r') as file:
            self.questions = file.readlines()

    def clearEvalResults(self):
        self.EvalResults = []
    
    def getEvalResults(self):
        result = eval.average_eval_results(self.EvalResults)
        print(result)
        return result
    
    def evalAll(self, questions_filename="questions.txt", userag_table_name:str=None, evalNum:int=100):
        self.loadQuestions(questions_filename)
        for question in self.questions[0:evalNum]:
            self.eval(question, userag_table_name)
        return eval.average_eval_results(self.EvalResults)

    def eval(self, question, userag_table_name:str=None)->eval.EvalResult:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        input_text = question         
        if userag_table_name:
            input_text += + "I will also provide some contexts, use it only when it is helpful(contexts can be not relavant at all)."
            topk_rank_result = rag_app.get_documents(userag_table_name, question, 5)
            for i, result in enumerate(topk_rank_result):
                input_text += f"Context {i+1}: {result['text']}"
        
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
        inputs = {key: value.to(device) for key, value in inputs.items()}

        model = self.model
        model.to(device)
        model.eval()

        with torch.no_grad():
            outputs = model(**inputs)

            # Convert logits to token ids (if applicable)
            token_ids = torch.argmax(outputs.logits, dim=-1)

            # Decode the token ids to text
            output_text = self.tokenizer.decode(token_ids[0], skip_special_tokens=True)


        # Print only if random number is less than 0.1
        
        print(f"Question: {question}\n")
        print(f"Answer: {output_text}\n")
        eval_result = self.llmEvaluator.evaluate(question, output_text)
        print(f"Eval Result: {eval_result.to_dict()}\n")

        self.EvalResults.append(eval_result)
        return self.EvalResults[-1]
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluate a language model.")
    parser.add_argument("--model_name", type=str, required=True, help="The name or path of the model to evaluate.")
    parser.add_argument("--questions_filename", type=str, default="eval/questions.txt", help="The filename containing the questions.")
    parser.add_argument("--userag_table_name", type=str, help="The userag table name for context retrieval.")
    parser.add_argument("--eval_num", type=int, default=10, help="The number of questions to evaluate.")

    args = parser.parse_args()

    evaluator = Evaluator(args.model_name)
    r=evaluator.evalAll(questions_filename=args.questions_filename, userag_table_name=args.userag_table_name, evalNum=args.eval_num)
    print(r.to_dict())
    