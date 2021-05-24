from flask import Flask, request, json, Response
from pymongo import MongoClient

class MongoDB():
    def __init__(self, data):
    #   self.client = MongoClient("mongodb://mongo_service:27017/")
        self.client = MongoClient("mongodb://localhost:5000")
        database = data["database"]
        collection = data["collection"]
        cursor = self.client[database]
        self.collection = cursor[collection]
        self.data = data
        
    def read(self):
        documents = self.collection.find()
        output = [{item: data[item] for item in data if item != "_id"} for data in documents]
        return output

    def write(self, data):
        new_doc = data["Document"]
        response = self.collection.insert_one(new_doc)
        output = {
            "Status": "Sucessfully Inserted",
            "Document_ID": str(response.inserted_id)
        }
        return output

    def update(self):
        filt = self.data["Filter"]
        updated_data = {"$set": self.data["DataToBeUpdated"]}
        response = self.collection.update_one(filt, updated_data)
        output = {
            "Status": "Successfully Update" if response.modified_count > 0 else "Nothing was updated."
        }
        return output

    def delete(self, data):
        filt = data['Filter']
        response = self.collection.delete_one(filt)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output    
