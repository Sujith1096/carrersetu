import urllib.request
import json
import os

def test_api_upload():
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Alex_Rivera_Resume.pdf")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="Alex_Rivera_Resume.pdf"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + pdf_bytes + (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="job_title"\r\n\r\n'
        f"Senior Full Stack Engineer\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="job_company"\r\n\r\n'
        f"Nexus Technologies\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="job_description"\r\n\r\n'
        f"Seeking a Senior Full Stack Engineer with strong React, TypeScript, Python, FastAPI, Docker, and PostgreSQL experience.\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")

    req = urllib.request.Request(
        "http://127.0.0.1:5173/api/analyze/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )

    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        data = json.loads(res.read().decode())
        print(f"API STATUS: 200 OK")
        print(f"Candidate: {data['candidate_name']}")
        print(f"ATS Score: {data['overall_score']}/100 ({data['match_rating']})")
        print(f"Matching Skills ({len(data['matching_skills'])}): {data['matching_skills'][:6]}")
        print(f"Missing Skills: {data['missing_skills']}")
        print(f"Recommendations: {len(data['recommendations'])} actionable items")
        print(f"Database ID assigned: #{data['id']}")

if __name__ == "__main__":
    test_api_upload()
