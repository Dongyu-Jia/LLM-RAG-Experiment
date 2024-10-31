
# Eval Method

We will evaluate our RAG system in 3 ways:
*  Retriver Evaluation: We focus on how good the retriver is, and evaluate the performance of the tok k result retrived by the retriver.
*  Generator Evaluation: Based on the list of retrival result and query, how good is the generation result.
*  End to end Evaluation:  Based on the query, how good is the rag system compared to no-rag LLM.

# Data set

One can potentially use open data set for evaluation. You can search tshe data set on hugging face, data set below offer a 3 piece information can be used for training or eval:
*  the document offering context
*  A question based on document
*  An answer (or a list of acceptable answers)

Data set names:
* TriviaQA
* HotpotQA
* FEVER
* Wizard of Wikipedia
* Natural Questions


# Use benchmark to evaluate

Benchamark is a collection of code+data that can be used to integrate with another algorithm/model to evaluate the performance. Quite a few papers already published data and code for evaluation.

# Our Evaluation

For Generator Evaluation:

* Benchmark method:
  * [Benchmarking Large Language Models in Retrieval-Augmented Generation](https://ojs.aaai.org/index.php/AAAI/article/view/29728); code: https://github.com/chen700564/RGB
    * This benchmark provide data as eval algorithm, and evaluate on the models'a ability on:
      *  "reject answer if there are not sufficient information" 
      *  "error dedection when the input is self conflicting"
      *  "accuracy with noise"
   *  [CRAG](https://dl.acm.org/doi/pdf/10.1145/3701228)
      *  [Challenge](https://www.aicrowd.com/challenges/meta-comprehensive-rag-benchmark-kdd-cup-2024) 


For Retriver Evaluation:
* [Evaluating Retrieval Quality in Retrieval-Augmented Generation](https://dl.acm.org/doi/pdf/10.1145/3626772.3657957) code: https://github.com/alirezasalemi7/eRAG
  * we can borrow the key idea in the paper: evaluate the retrieval result based on if the generated answer used it. (In paper it feed LLM with one doc vs all doc, and compare the output to derive a relavance score)
    * To compare two text response similarity, we can use embeding similarity or token based similarity.
* Assume we already split the data in to sections of test. we can generate question based on each section, use the question as query and see if retriever was able to retrive the result.
* Assume the retriever returns the top K result, we can ask LLM to score the relevance for each result. 


For Overall Evaluation:
*  We use LLM to evaluate the result on different perspectives. (see DirectLLMEvalWithOpenAI in eval.py)
*  We use a small number of defined questions and use human evaluation 