import subprocess
import json
import difflib
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

class CodingSystem:
    def __init__(self, repo_root: str = '.'):
        self.repo_root = Path(repo_root)
        self.memory_short: List[Dict] = []
        self.max_iterations = 5
        
        self.client = OpenAI(
            api_key=os.getenv('GROQ_API_KEY'),
            base_url='https://api.groq.com/openai/v1'
        )

    def iterative_loop(self, task: str):
        self.memory_short.clear()
        self.memory_short.append({'step': 'start', 'task': task})
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
                messages=[
                    {'role': 'system', 'content': 'You are Groks Baby - a precise coding agent. Always respond with a clear git-style diff when making code changes.'},
                    {'role': 'user', 'content': f'Task: {task}\nOutput only a git unified diff or clear explanation.'}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            result = response.choices[0].message.content.strip()
            self.memory_short.append({'step': 'complete', 'result': result})
            return result
        except Exception as e:
            return f'Error: {str(e)}'
