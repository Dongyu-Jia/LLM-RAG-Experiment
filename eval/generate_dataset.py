import os
import openai
from datasets import Dataset
from datasets import load_from_disk, concatenate_datasets
from huggingface_hub import HfApi, HfFolder


# Path to the questions file
questions_file = '/home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/questions.txt'

# Read questions from the file
with open(questions_file, 'r') as file:
    questions = file.readlines()
client =  openai.OpenAI()
# Generate responses using OpenAI's API
responses = []
for i, question in enumerate(questions[0:1000]):
    # Check if the file already exists, if so, skip to the next 50
    if os.path.exists(f'/home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/generated_dataset_{(i//50+1)*50}'):
        print(f"File for {i+1} already exists, skipping.")
        continue

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {
                    "role": "user",
                    "content": question + ";If the question does not provide enough context, please say it does not provide enough context",
                },
            ],
        max_tokens=250
    )
    responses.append(response.choices[0].message.content.strip())
    print(f"Processed {i+1}/{len(questions[0:1000])} questions")

    # Save to disk every 50 records
    if (i + 1) % 50 == 0:
        data = {
            'question': questions[:i+1],
            'answer': responses
        }
        formatted_data = [
            {"prompt": q.strip(), "completion": a}
            for q, a in zip(data['question'], data['answer'])
        ]
        dataset = Dataset.from_list(formatted_data)
        dataset.save_to_disk(f'/home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/generated_dataset_{i+1}')


# Merge all saved datasets into one

# List all saved dataset paths
dataset_paths = [
    f'/home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/generated_dataset_{i}'
    for i in range(50, 1001, 50)
]

# Load and concatenate datasets
datasets = [load_from_disk(path) for path in dataset_paths]
merged_dataset = concatenate_datasets(datasets)

# Split the merged dataset into train and eval sets
train_test_split = merged_dataset.train_test_split(test_size=0.1)

# Save the train and eval datasets to disk in one location
train_test_split.save_to_disk('/home/ubuntu/dongyuj/LLM-RAG-Experiment/eval/train_eval_dataset')

