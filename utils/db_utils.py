from firebase_functions import https_fn, firestore_fn, scheduler_fn
from firebase_admin import initialize_app, firestore
import google.cloud.firestore
from utils.time_utils import convert_to_12_hour_format
import utils.constants as constants
from datetime import date, datetime

def get_data_from_document(collection: str, document: str) -> any:
    """
    Reads data from a Firestore document.

    Args:
        collection (str): The name of the Firestore collection.
        document (str): The name of the Firestore document.
    Returns:
        any: The data from the Firestore document as a dictionary, or None if the document does not exist.

    """
    # Access Firestore
    db: google.cloud.firestore.Client = firestore.client()

    # Get a reference to the document
    document_reference = db.collection(collection).document(document)

    # Get the document
    document = document_reference.get()

    # Make sure it exists
    if not document.exists:
        print("Document does not exist.")
        return

    # Get the document data
    data = document.to_dict()

    return data

def write_data_to_document(collection: str, doc_id: str, data: dict, merge: bool = False) -> None:
    """
    Writes data to a Firestore document.

    Args:
        collection (str): The name of the Firestore collection.
        doc_id (str): The document ID to write to.
        data (dict): The data to write to the document.
        merge (bool, optional): Whether to merge the new data with existing data.
                                 Defaults to False, which overwrites the document.

    Returns:
        None
    """
    db = firestore.client()
    doc_ref = db.collection(collection).document(doc_id)

    try:
        if merge:
            doc_ref.set(data, merge=True)  # Merges with existing data
        else:
            doc_ref.set(data)  # Overwrites the document

        #print(f"Document '{doc_id}' written to collection '{collection}' successfully.")
    except Exception as e:
        print(f"Error writing to document '{doc_id}' in collection '{collection}': {e}")

def batch_write_month(collection_name: str, data: list) -> None:

    db = firestore.client()
    batch = db.batch()
    upserted_ids = set() 

    try:

        for prayer_day in data:
            print(prayer_day)
            document_id = prayer_day.date
            upserted_ids.add(document_id)
            doc_ref = db.collection(collection_name).document(document_id)

            # Convert times to 12-hour format
            prayer_times_data = {
                'fajr': convert_to_12_hour_format(prayer_day.fajr),
                'sunrise': convert_to_12_hour_format(prayer_day.sunrise),
                'dhuhr': convert_to_12_hour_format(prayer_day.dhuhr),
                'asr': convert_to_12_hour_format(prayer_day.asr),
                'maghrib': convert_to_12_hour_format(prayer_day.maghrib),
                'isha': convert_to_12_hour_format(prayer_day.isha),
                'date': prayer_day.date
            }

            batch.set(doc_ref, prayer_times_data)
        
        batch.commit()
        #print(f"Uploaded prayer times for {len(data)} days to Firebase.")

        # Step 2: Delete non-upserted documents
        existing_docs = db.collection(collection_name).stream()
        delete_batch = db.batch()

        for doc in existing_docs:
            if doc.id not in upserted_ids:
                delete_batch.delete(doc.reference)

        delete_batch.commit()  # Commit the deletions
        #print(f"Deleted documents not in the upserted list from '{collection_name}'.")

    except Exception as e:
        print(f"Error writing to Firestore from inside batch_write_month: {e}")
        return

def update_monthly_storage():

    # Connect to Firestore Database
    db: google.cloud.firestore.Client = firestore.client()

    # Connect to Collection hosting year of prayer times
    prayer_times_ref = db.collection(constants.NEW_TIMES_COLLECTION)

    # Get Date
    today = date.today()
    month = today.month
    year = today.year

    # Set Date Query parameters
    first_day = f"{year}-{month:02d}-01"  # "YYYY-MM-01"
    last_day = f"{year}-{month:02d}-31"   # "YYYY-MM-31"

    # Build Query
    query = (prayer_times_ref
         .where(filter=firestore.FieldFilter("date", ">=", first_day))
         .where(filter=firestore.FieldFilter("date", "<=", last_day)))

    # Execute Query
    documents = [doc.to_dict() for doc in query.stream()]

    # Create Storage for documents we want to keep
    upserted_ids = set()

    # Upload documents to collection
    batch = db.batch()
    for doc in documents:
        doc_id = doc["date"]
        upserted_ids.add(doc_id)
        doc_ref = db.collection("Test_Collection_1").document(doc_id)
        batch.set(doc_ref, doc, merge=True)
    batch.commit()

    existing_docs = db.collection("Test_Collection_1").stream()
    delete_batch = db.batch()

    for doc in existing_docs:
        if doc.id not in upserted_ids:
            delete_batch.delete(doc.reference)

    delete_batch.commit()  # Commit the deletions
