import requests
import json

def test_document_upload():
    """Test document upload API with question3.pdf"""

    # API endpoint
    url = "http://127.0.0.1:8003/documents/upload"

    # Prepare the file and data
    files = {
        'file': ('question3.pdf', open('question3.pdf', 'rb'), 'application/pdf')
    }

    data = {
        'user_id': '83874cd4-507c-4fad-9641-efc19beafd18',
        'document_type': 'question'
    }

    try:
        print("Testing document upload API...")
        print(f"Uploading file: question3.pdf")
        print(f"User ID: {data['user_id']}")
        print(f"Document Type: {data['document_type']}")

        # Make the request
        response = requests.post(url, files=files, data=data)

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ Upload Successful!")
            print("Response:", json.dumps(result, indent=2))
        else:
            print("\n❌ Upload Failed!")
            print("Error Response:", response.text)

    except Exception as e:
        print(f"\n❌ Error during upload: {e}")

    finally:
        # Close the file
        if 'file' in files:
            files['file'][1].close()

if __name__ == "__main__":
    test_document_upload()
