import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('gender-fair-82d21-firebase-adminsdk-xzaw3-9e24d547ea.json')
firebase_admin.initialize_app(cred)

def delete_field_in_batches(collection_name, batch_size=100):
    db = firestore.client()
    last_doc = None

    while True:
        query = db.collection(collection_name).limit(batch_size)
        if last_doc:
            query = query.start_after(last_doc)

        docs = query.stream()
        num_docs = 0

        for doc in docs:
            num_docs += 1
            if 'trustees_Sscore' in doc.to_dict():
                doc.reference.update({
                    'trustees_Sscore': firestore.DELETE_FIELD
                })

        if num_docs < batch_size:
            break  # No more documents left

        last_doc = doc  # Set the last document for the next batch's start_after

delete_field_in_batches('non-for-profits')
