import torch
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer
import eval
import os, sys
folder_a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rag'))  

# Add the folder path to sys.path  
sys.path.insert(0, folder_a_path)  

import app as rag_app

class Evaluator:
    def __init__(self, model_name:str):
        self.tokenizer = AutoTokenizer.from_pretrained("llama3_2_batch_2_tuned_model_tokenizer/")
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.EvalResults = []
        self.llmEvaluator=eval.DirectLLMEvalWithOpenAI()

    def clearEvalResults(self):
        self.EvalResults = []
    
    def getEvalResults(self):
        result = eval.average_eval_results(self.EvalResults)
        print(result)
        return result

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
        self.EvalResults.append(self.llmEvaluator.eval(question, output_text))
        
    
    