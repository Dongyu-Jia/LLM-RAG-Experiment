import pandas as pd
import sys ; sys.path.append("..")
import os  
import retriever_eval as retriever_eval
import generator_eval as generator_eval
import eval as eval

def main():
    # get the list of questions
    with open('questions.txt', 'r') as file:
        questions = file.readlines()

    df = pd.DataFrame()

    df['question'] = [q for q in questions[500:1500]]

    # get the list of self-contained

    openAI=eval.OpenAIChatCompletionWrapper()

    conn = retriever_eval.getConnection()
    evaluator = generator_eval.Evaluator("../finetune/Llama-3.2-1B-Instruct-SFT")

    # Define the number of questions to evaluate at a time
    batch_size = 5

    # Evaluate questions in batches
    for start in range(0, len(df['question']), batch_size):
        if os.path.exists(f'result/evaluation_results_{start}.csv'):
            continue
        end = start + batch_size
        df_batch = pd.DataFrame({
            'question': pd.Series(dtype='str'),
            'self_contained': pd.Series(dtype='bool'),
            'retrieved_relavant_info_rank': pd.Series(dtype='int'),
            'retrieved_info': pd.Series(dtype='str'),
            'baseline_response': pd.Series(dtype='str'),
            'finetune_response': pd.Series(dtype='str'),
            'baseline_eval': pd.Series(dtype='object'),
            'finetune_eval': pd.Series(dtype='object'),
            'baseline_with_rag_response': pd.Series(dtype='str'),
            'finetune_with_rag_response': pd.Series(dtype='str'),
            'baseline_with_rag_eval': pd.Series(dtype='object'),
            'finetune_with_rag_eval': pd.Series(dtype='object'),
        })
        df_batch['question'] = df['question'][start:end]
        
        for i, q in enumerate(df_batch['question']):
            try:
                df_batch.at[i, 'self_contained'] = openAI.returnTF("Does this question provide enough context to be answered? Questions:" + q)
                df_batch.at[i, 'retrieved_relavant_info_rank'] = retriever_eval.search_question_and_get_order(conn, "document_semantic_split", q)
                re, ev = evaluator.eval(q, None, True)
                df_batch.at[i, 'baseline_response'], df_batch.at[i, 'baseline_eval'] = re, ev.to_dict()
                re, ev = evaluator.eval(q, None, False)
                df_batch.at[i, 'finetune_response'], df_batch.at[i, 'finetune_eval'] = re, ev.to_dict()
                re, ev = evaluator.eval(q, "document_semantic_split", True)
                df_batch.at[i, 'baseline_with_rag_response'], df_batch.at[i, 'baseline_with_rag_eval'] = re, ev.to_dict()
                re, ev = evaluator.eval(q, "document_semantic_split", False)
                df_batch.at[i, 'finetune_with_rag_response'], df_batch.at[i, 'finetune_with_rag_eval'] = re, ev.to_dict()
                df_batch.at[i, 'retrieved_info'] = evaluator.getRagContext("document_semantic_split", q)
            except Exception as e:
                print(f"Error: {e}")
                continue    
        # Append the batch results to the CSV file
        df_batch.to_csv(f'result/evaluation_results_{start}.csv', index=False)

if __name__ == "__main__":
    main()