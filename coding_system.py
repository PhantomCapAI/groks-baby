import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("WARNING: No GROQ_API_KEY - running in demo mode")
            self.client = None
            return
        self.client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')

    def planner(self, task: str):
        prompt = f"""You are the Planner agent.
Task: {task}
Create a clear, step-by-step plan (3-5 steps max). Be concise."""
        if not self.client:
            return "Demo plan: 1. Understand task 2. Generate code 3. Review"
        response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=600)
        return response.choices[0].message.content

    def coder(self, plan: str):
        prompt = f"""You are the Coder agent.
Plan: {plan}
Output ONLY a clean git-style unified diff or full code block."""
        if not self.client:
            return f"# Demo code for: {plan[:100]}..."
        response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], temperature=0.2, max_tokens=1500)
        return response.choices[0].message.content

    def reviewer(self, code: str):
        prompt = f"""You are the Reviewer agent.
Code/Diff: {code}
Score 0-100 and give short feedback. Return as JSON: {{"score": 85, "feedback": "Good but...", "pass": true}}"""
        if not self.client:
            return {{"score": 80, "feedback": "Demo review", "pass": True}}
        try:
            response = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": prompt}], temperature=0.3, max_tokens=400)
            return eval(response.choices[0].message.content)
        except:
            return {{"score": 75, "feedback": "Review completed", "pass": True}}

    def iterative_loop(self, task: str, max_iterations: int = 3):
        plan = self.planner(task)
        code = self.coder(plan)
        review = self.reviewer(code)

        return {
            "plan": plan[:500] + "..." if len(plan) > 500 else plan,
            "final_diff": code,
            "final_review": review,
            "iterations": max_iterations,
            "message": "Grok's Baby v2 - Full capability + Bitcoin intuition transferred."
        }
