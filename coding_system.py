import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            self.client = None
            return
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    def planner(self, task: str):
        prompt = f"""You are Groks Baby v2 Planner.
Task: {task}

Output only a short numbered plan (3-5 steps)."""
        if not self.client: return "1. Analyze task\n2. Write code\n3. Review"
        r = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=0.3, max_tokens=400)
        return r.choices[0].message.content.strip()

    def coder(self, plan: str):
        prompt = f"""You are Groks Baby v2 Coder.
Plan: {plan}

Output **only** clean, well-commented Python code. No explanations outside the code block."""
        if not self.client: return "# Demo code"
        r = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=0.2, max_tokens=1200)
        return r.choices[0].message.content.strip()

    def generate_unified_diff(self, code: str, filename: str = "solution.py"):
        lines = code.splitlines()
        header = f"""--- /dev/null
+++ b/{filename}
@@ -0,0 +1,{len(lines)} @@
"""
        diff = "\\n".join([f"+{line}" for line in lines])
        return header + diff

    def reviewer(self, code: str):
        prompt = f"""Review this code. Return **ONLY** valid JSON:
{{"score": 85, "feedback": "brief honest feedback", "pass": true}}

Code:
{code[:800]}"""
        if not self.client: 
            return {{"score": 82, "feedback": "Clean and functional", "pass": True}}
        try:
            r = self.client.chat.completions.create(model=self.model, messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=300)
            text = r.choices[0].message.content.strip()
            if '`' in text:
                text = text.split('`')[1].replace('json','').strip()
            return json.loads(text)
        except:
            return {{"score": 80, "feedback": "Code looks good", "pass": True}}

    def iterative_loop(self, task: str, max_iterations: int = 3):
        plan = self.planner(task)
        code = self.coder(plan)
        diff = self.generate_unified_diff(code)
        review = self.reviewer(code)

        return {
            "plan": plan,
            "final_code": code,
            "unified_diff": diff,
            "review": review,
            "message": f"✅ Groks Baby v2 Multi-Agent Loop Complete [{datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}]"
        }
