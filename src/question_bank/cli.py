import subprocess


print("Generating test questions for A1 level...")
subprocess.run(["python", "generate_test.py", "--level", "A1"])

print("Generating test questions for A2 level...")
subprocess.run(["python", "generate_test.py", "--level", "A2"])

print("Generating test questions for B1 level...")
subprocess.run(["python", "generate_test.py", "--level", "B1"])

print("Generating test questions for B2 level...")
subprocess.run(["python", "generate_test.py", "--level", "B2"])

print("Generating test questions for C1 level...")
subprocess.run(["python", "generate_test.py", "--level", "C1"])

print("Uploading test questions...")
subprocess.run(["python", "upload_questions.py"])