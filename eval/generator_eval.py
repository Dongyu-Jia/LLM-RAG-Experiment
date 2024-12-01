import torch
from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM, AutoTokenizer
import eval
import os, sys
folder_a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rag'))  

# Add the folder path to sys.path  
sys.path.insert(0, folder_a_path)  

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    pipeline,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer


import app as rag_app
import argparse

class Evaluator:
    def __init__(self, peftModel:str):
        base_model_name = "unsloth/Llama-3.2-1B-Instruct"
        new_model = peftModel
        device_map = {"": 0}

        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            low_cpu_mem_usage=True,
            return_dict=True,
            torch_dtype=torch.float16,
            device_map=device_map,
        )
        new_model_path = os.path.abspath(new_model)
        self.model = PeftModel.from_pretrained(self.base_model, new_model_path)
        self.model = self.model.merge_and_unload()

        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
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
    
    def evalAll(self, questions_filename="questions.txt", userag_table_name:str=None, evalNum:int=100, useBaseModel=True):
        self.loadQuestions(questions_filename)
        for question in self.questions[0:evalNum]:
            self.eval(question, userag_table_name, useBaseModel)
        return eval.average_eval_results(self.EvalResults)
    
    def getRagContext(self, userag_table_name:str=None, question="", limit=5):
        input_text = ""
        topk_rank_result = rag_app.get_documents(userag_table_name, question, limit)
        for i, result in enumerate(topk_rank_result):
            if result.text in input_text:
                continue
            input_text += f"Context {i+1}: {result.text}\n"
        return input_text


    def eval(self, question, userag_table_name:str=None, useBaseModel=True)->eval.EvalResult:
        input_text = question         
        if userag_table_name:
            input_text += "I will also provide some contexts, use it only when it is helpful(contexts can be not relavant at all). Answer within 400 words.\n"
            input_text += self.getRagContext(userag_table_name, question, 5) 
        
        prompt = input_text

        if not useBaseModel:
            modelForEval = self.model
        else:
            modelForEval = self.base_model
        max_length = 5000
        prompt_words = prompt.split()
        if len(prompt_words) > max_length:
            prompt = ' '.join(prompt_words[:2800])
        pipe = pipeline(task="text-generation", model=modelForEval, tokenizer=self.tokenizer, max_length=max_length)
        result = pipe(f"<s>[INST] {prompt} [/INST]")
        output_text = result[0]["generated_text"]

        # Print only if random number is less than 0.1
        
        PRINT_PROB = 0.1
        eval_result = self.llmEvaluator.evaluate(question, output_text)
        if torch.rand(1).item() < PRINT_PROB:
            print(f"Question: {prompt}\n")
            print(f"Answer: {output_text}\n")
            print(f"Eval Result: {eval_result.to_dict()}\n")

        self.EvalResults.append(eval_result)
        return output_text, self.EvalResults[-1]
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Evaluate a language model.")
    parser.add_argument("--model_name", type=str, required=True, help="The name or path of the model to evaluate.")
    parser.add_argument("--questions_filename", type=str, default="eval/questions.txt", help="The filename containing the questions.")
    parser.add_argument("--userag_table_name", type=str, help="The userag table name for context retrieval.")
    parser.add_argument("--eval_num", type=int, default=1, help="The number of questions to evaluate.")

    args = parser.parse_args()

    evaluator = Evaluator(args.model_name)
    r=evaluator.evalAll(questions_filename=args.questions_filename, userag_table_name=args.userag_table_name, evalNum=args.eval_num)
    print(r.to_dict())
    