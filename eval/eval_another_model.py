import os
import pandas as pd
import argparse
import retriever_eval as retriever_eval
import generator_eval as generator_eval
import eval as eval

def main():
    parser = argparse.ArgumentParser(description='Process some CSV files.')
    parser.add_argument('input_folder', type=str, help='Path to the input folder')
    parser.add_argument('output_folder', type=str, help='Path to the output folder')
    parser.add_argument('--model', type=str, default='Llama-3.2-1B-Instruct-SFT', help='Model name')
    parser.add_argument('--column_prefix', type=str, default='finetune', help='Column prefix')
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    evaluator = generator_eval.Evaluator("../finetune/" + args.model)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            output_path = os.path.join(output_folder, filename)
            if os.path.exists(output_path):
                print(f"File {output_path} already exists. Skipping.")
                continue
            input_path = os.path.join(input_folder, filename)
            df = pd.read_csv(input_path)
            
            df[args.column_prefix + '_response'] = pd.Series(["" for _ in range(len(df))], dtype="str")
            df[args.column_prefix + '_eval'] =  pd.Series([{} for _ in range(len(df))], dtype='object')
            df[args.column_prefix + '_with_rag_response'] = pd.Series(["" for _ in range(len(df))], dtype="str")
            df[args.column_prefix + '_with_rag_eval'] =  pd.Series([{} for _ in range(len(df))], dtype='object')
            
            for i, q in enumerate(df['question']):
                try:
                    re, ev = evaluator.eval(q, None, False)
                    
                    df.at[i, args.column_prefix +'_response'], df.at[i, args.column_prefix+'_eval'] = re, ev.to_dict()
                    re, ev = evaluator.eval(q, "document_semantic_split", False)
                    df.at[i, args.column_prefix+'_with_rag_response'], df.at[i, args.column_prefix+'_with_rag_eval'] = re, ev.to_dict()
                except Exception as e:
                    print(f"Error: {e}")
                    continue    
            
            output_path = os.path.join(output_folder, filename)
            df.to_csv(output_path, index=False)

# Run the script
# nohup python eval_another_model.py ./result ./result2 --model Llama-3.2-1B-Instruct-SFT --column_prefix Batch-2-Step-60-lr-2e_4 > eval2.log 2>&1 &

if __name__ == '__main__':
    main()