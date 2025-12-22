import requests
import uuid

LANGFLOW_API_KEY = "sk-8zTqhnMe8iNesxvqtBpR3dsBwpUCyKBQvHM-Q4s68iA"
BASE_URL = "http://172.17.0.1:7860"
FLOW_ID = "17f0755a-bee6-4380-8f1d-84aef615ac0d"

headers = {"x-api-key": LANGFLOW_API_KEY}

def upload_pdf(file):
    response = requests.post(
        f"{BASE_URL}/api/v2/files",
        headers=headers,
        files={"file": file}
    )
    response.raise_for_status()
    print(f"FILE PATH: {response.json()}")
    return response.json()["path"]

def generate_mcqs_from_langflow(pdf_path, num_questions=5):
    session_id = str(uuid.uuid4())

    payload = {
        "output_type": "chat",
        "input_type": "text",
        "input_value": f"Generate {num_questions} questions",
        "session_id": session_id,
        "tweaks": {
            "File-hacxY": {
                "path": [pdf_path]
            },
            "PromptNodeIdIfAny": {
                "count": num_questions
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/run/{FLOW_ID}",
        headers={"Content-Type": "application/json", **headers},
        json=payload
    )
    print("STATUS", response.status_code)
    print("BODY", response.text)

    response.raise_for_status()
    data = response.json()

    mcq_output = data["outputs"][0]["outputs"][0]["results"]["message"]["data"]["content"]

    return mcq_output
