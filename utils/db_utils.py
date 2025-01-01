from firebase_functions import https_fn, firestore_fn, scheduler_fn
from firebase_admin import initialize_app, firestore
import google.cloud.firestore

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
    else: print("Document exists.")

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

        print(f"Document '{doc_id}' written to collection '{collection}' successfully.")
    except Exception as e:
        print(f"Error writing to document '{doc_id}' in collection '{collection}': {e}")
