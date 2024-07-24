import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
import json
from openai import OpenAI
import time

client = OpenAI(api_key=os.getenv("OPENAI_GENDERFAIR_KEY"))

cred = credentials.Certificate(
    "gender-fair-82d21-firebase-adminsdk-xzaw3-9b1027afcf.json"
)
firebase_admin.initialize_app(cred)
db = firestore.client()

BATCH_SIZE = 5000
NUM_BATCHES = 5

categories = [
    "Animals",
    "Arts",
    "Children",
    "College",
    "Community",
    "Needs",
    "Education",
    "Environmental",
    "Healthcare",
    "Hospital",
    "Hunger",
    "STEM",
    "Women",
    "Other",
]

def create_batch_input(docs, batch_number):
    filename = f"batch_input_{batch_number}.jsonl"
    with open(filename, "w") as f:
        for idx, (doc_id, data) in enumerate(docs):
            name = data.get("name", "")
            description_list = data.get("descriptions", [])
            combined_text = f"{name} " + " ".join(description_list)

            request = {
                "custom_id": doc_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-3.5-turbo-0125",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a helpful assistant that categorizes non-profit organizations. Please categorize the following organization and accompanying summary into one of these categories: {', '.join(categories)}. Respond with only the category name.",
                        },
                        {"role": "user", "content": combined_text},
                    ],
                    "max_tokens": 50,
                },
            }
            json.dump(request, f)
            f.write("\n")
    return filename


def process_batch(batch_input_filename):
    with open(batch_input_filename, "rb") as file:
        batch_file = client.files.create(file=file, purpose="batch")

    batch = client.batches.create(
        input_file_id=batch_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )

    while True:
        batch_status = client.batches.retrieve(batch.id)
        if batch_status.status == "completed":
            break
        elif batch_status.status in ["failed", "expired", "cancelled"]:
            raise Exception(f"Batch failed with status: {batch_status.status}")
        time.sleep(60)

    output_file = client.files.content(batch_status.output_file_id)

    for line in output_file.text.split("\n"):
        if line.strip():
            result = json.loads(line)
            doc_id = result["custom_id"]
            category = (
                result["response"]["body"]["choices"][0]["message"]["content"]
                .strip()
                .lower()
            )

            if category in [c.lower() for c in categories]:
                db.collection("non-for-profits").document(doc_id).update(
                    {"category": category}
                )


def main():
    non_profits_ref = db.collection("non-for-profits")
    all_docs = list(non_profits_ref.stream())

    docs_to_process = [
        (doc.id, doc.to_dict()) for doc in all_docs
    ]
    
    docs_done = 0
    for batch_number in range(NUM_BATCHES):
        start_idx = batch_number * BATCH_SIZE
        end_idx = min((batch_number + 1) * BATCH_SIZE, len(docs_to_process))
        batch_docs = docs_to_process[start_idx:end_idx]

        if not batch_docs:
            print(f"No more documents to process in batch {batch_number + 1}")
            break

        print(f"Processing batch {batch_number + 1} with {len(batch_docs)} documents")

        batch_input_filename = create_batch_input(batch_docs, batch_number)
        process_batch(batch_input_filename)

        docs_done += len(batch_docs)
        print(
            f"Completed batch {batch_number + 1}. Total processed documents: {docs_done}"
        )

    print("All batches completed.")


if __name__ == "__main__":
    main()
    firebase_admin.delete_app(firebase_admin.get_app())
