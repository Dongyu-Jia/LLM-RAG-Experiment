
export PGPASSWORD='CS230password'  
psql -U postgres -d postgres -h 'database-1.cdi4gywsaigf.us-east-2.rds.amazonaws.com' -p 5432
#Password: CS230password


nohup /home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_semantic_split > document_semantic_split.log 2>&1 &  
#[1] 60538
nohup /home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_recursive_split_rst_separator_1000_50  > document_recursive_split_rst_separator_1000_50_output.log 2>&1 &  
# [2] 60598
nohup /home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_recursive_split_default_300_50  > document_recursive_split_default_300_50_output.log 2>&1 &  
#[3] 60659


