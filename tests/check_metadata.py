import sys
import os


# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    PROJECT_ROOT
)


from rag.vectorstore.chroma import get_vectorstore



db = get_vectorstore()


data = db.get(
    limit=10,
    include=[
        "metadatas"
    ]
)


for metadata in data["metadatas"]:

    print("\n----------------")
    print(metadata)