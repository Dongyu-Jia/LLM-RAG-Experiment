import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

# URL for the Pandas documentation homepage
base_url = "https://pandas.pydata.org/pandas-docs/stable/"

# Example: Documentation section for Pandas DataFrame methods
docs_url = base_url + "reference/frame.html"

# Send a request to the documentation page
response = requests.get(docs_url)
soup = BeautifulSoup(response.content, "lxml")


data = []
for method_section in soup.find_all("tr"):
    col_num = method_section.find_all('td')
    if (len(col_num) == 2):
      title = method_section.find_all('td')[0].get_text(strip=True) or "N/A"
    #   print(title)
      description = method_section.find_all('td')[1].get_text(strip=True) or "N/A"
    #   print(description)
      # Append the section and content to the data list
      data.append({"section": title, "content": description})
      # Pause to avoid overloading the server
      time.sleep(1)
    else:
      continue
  
  # Save as JSON
with open("./raw_pandas_docs.json", "w") as json_file:
    json.dump(data, json_file, indent=4)
    
llama_conversations = { "conversations": []}
for entry in data:
    message = [
        {"role": "user", "content": entry["section"]},     # User's message
        {"role": "assistant", "content": entry["content"]} # Assistant's response
    ]
    llama_conversations["conversations"].append(message)

with open("./formatted_pandas_docs.json", "w") as f:
    json.dump(llama_conversations, f, indent=4)