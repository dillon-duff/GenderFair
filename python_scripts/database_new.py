from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)

# Firestore setup
cred = credentials.Certificate("gender-fair-82d21-firebase-adminsdk-xzaw3-9e24d547ea.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

class DatabaseManager:
    def __init__(self):
        self.db = firestore.client()

    def get_company_by_eid(self, eid):
        # Firestore query to fetch a company by EID
        companies_ref = self.db.collection('non-for-profits')
        query_ref = companies_ref.where('ein', '==', eid)
        docs = query_ref.stream()
        for doc in docs:
            print(doc.to_dict)
            return doc.to_dict()
        return None

    def get_all_companies(self):
        # Firestore query to fetch all companies
        companies_ref = self.db.collection('non-for-profits')
        docs = companies_ref.stream()
        companies = [doc.to_dict() for doc in docs]
        return companies

    def search_company_by_name(self, name):
        # Firestore query to perform a flexible search for companies by name
        companies_ref = self.db.collection('non-for-profits')
        query_ref = companies_ref.where('name', '>=', name).where('name', '<=', name + '\uf8ff')
        docs = query_ref.stream()
        companies = [doc.to_dict() for doc in docs]
        return companies

# Flask endpoints
@app.route('/company/<eid>', methods=['GET'])
def get_company(eid):
    db_manager = DatabaseManager()
    return jsonify(db_manager.get_company_by_eid(eid))

@app.route('/companies', methods=['GET'])
def get_companies():
    db_manager = DatabaseManager()
    return jsonify(db_manager.get_all_companies())

@app.route('/search', methods=['GET'])
def search_company():
    name = request.args.get('name')
    db_manager = DatabaseManager()
    return jsonify(db_manager.search_company_by_name(name))

if __name__ == '__main__':
    app.run()