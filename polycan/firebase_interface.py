from polycan import db
from polycan.log import *
from tqdm import tqdm
import csv
import sys
import collections

def get_log(log_name):
    log_document = db.collection(u'logs').document(log_name)
    collection_ref = log_document.collection('log')
    collection = collection_ref.get()
    model_name = log_document.get().to_dict()['model']

    log = Log(log_name, model_name)
    for doc in collection:
        doc_dict = doc.to_dict()
        log_entry = LogEntry.from_dict(doc_dict)
        log.add(log_entry)
 
    return log    

def get_lognames():
    logs = db.collection(u'logs').get()
    log_names = []
    for log in logs:
        log_names.append(log.id)
    return log_names

def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0 
    try:
        with open("logs/"+path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            doc_ref = db.collection(u'logs').document(path[:-4]).collection('log')
            db.collection(u'logs').document(path[:-4]).set({u'model': '5055E'})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['Time'])
                batch.set(line_ref,{ u'pgn': int(line['PGN'], 16),
                                     u'destination': int(line['DA'], 16),
                                     u'source': int(line['SA'], 16),
                                     u'priority': int(line['Priority'], 16),
                                     u'time': float(line['Time']),
                                     u'data': line['Data']
                                     })  
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    return    

def get_known():
    known = {}
    collection_ref = db.collection(u'known')
    collection = db.collection(u'known').get()

    for doc in collection:
        doc_dict = doc.to_dict()
        pgn_object = Pgn.from_dict(doc_dict)

        params_list = []
        params = collection_ref.document(doc.id).collection(u'parameters').get()
        for param in params:
            param_dict = param.to_dict()
            params_list.append(param_dict)
        pgn_object.parameters = params_list
        known[pgn_object.pgn] = pgn_object
    return known
