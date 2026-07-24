from rag.generation.prompt import build_prompt

question = "What is the Leave Policy?"

context = """
Employees are entitled to Earned Leave,
Casual Leave,
and Sick Leave.
"""

prompt = build_prompt(question, context)

print(prompt)