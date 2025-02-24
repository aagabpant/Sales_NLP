import pandas as pd
from langchain.document_loaders import CSVLoader
from openai import OpenAI
import os
import time  # For adding delays if needed

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

#Load the CSV file
loader = CSVLoader(file_path=r"Data\Data Annotaters.csv")
documents = loader.load()

# Extract the statements from the CSV
statements = [doc.page_content for doc in documents]

# Define the prompt for the annotation task
system_prompt = """
You are a cybersecurity expert. Your task is to annotate the following cybersecurity incident statement based on the following categories:

1. **Type of Attack**: Choose from: Phishing, Ransomware, Unauthorized Access, DDoS, Malware, Insider Threat, Social Engineering, Zero-day Exploit, Data Breach, Email Spoofing, Spear-phishing.
2.**Date**: Choose the date from the statement.
3.**Target Organization**: Choose from the statement which oraganization is affected.
4. **Target**: Choose from: Employees, Financial Data, HR Database, Customer Data, IT Infrastructure, Executives, Web Applications, Supply Chain, Healthcare Records, R&D Data, Legal Data, Marketing Data, Sales Data, Customer Service, Logistics, Manufacturing, Research Data, Billing Systems, Inventory Systems, Communication Systems, if not from this list choose on your own
5. **Impact**: Choose from: Data Theft, Data Encryption, Service Disruption, Data Exposure, Credential Theft, Financial Loss, Operational Disruption, Reputation Damage, Legal Consequences, System Downtime, if not from this list choose on your own.

For each statement, provide the annotation in the following JSON format:
{
  "Type of Attack": "...",
  "Date": "...",
  "Target Organization":"...",
  "Target": "...",
  "Impact": "...",
}
"""


output_csv = "annotated_cybersecurity_statements.csv"

if not os.path.exists(output_csv):
    pd.DataFrame(columns=["Type of Attack", "Date","Target Organization","Target","Impact","Statement"]).to_csv(output_csv, index=False)

for statement in statements:
    try:
        response = client.chat.completions.create(
            model="gpt-4",  
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Statement: {statement}"
                }
            ]
        )

        annotation_response = response.choices[0].message.content

        try:
            annotation = eval(annotation_response) 
            annotation["Statement"] = statement 

            print("Adding to CSV:", annotation)

            df = pd.DataFrame([annotation])
            df.to_csv(output_csv, mode='a', header=not os.path.exists(output_csv), index=False)

            print(f"Processed statement: {statement}")
        except Exception as e:
            print(f"Error parsing response for statement: {statement}. Error: {e}")
    except Exception as e:
        print(f"Error processing statement: {statement}. Error: {e}")

    time.sleep(1)  

print("Annotation complete! Annotated data saved to 'annotated_cybersecurity_statements.csv'.")