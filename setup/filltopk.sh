#!/bin/bash  

/home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_semantic_split --filltopkranks > document_semantic_split_top_k.log 2>&1 
/home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_recursive_split_rst_separator_1000_50 --filltopkranks > document_recursive_split_rst_separator_1000_50_output_top_k.log 2>&1 
/home/ubuntu/miniconda/envs/rag-simplify/bin/python /home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/retriever_eval.py document_recursive_split_default_300_50 --filltopkranks > document_recursive_split_default_300_50_output_top_k.log 2>&1 
