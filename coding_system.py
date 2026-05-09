import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

class ProjectMemory:
    def __init__(self):
        self.base_dir = Path('project_memory')
        self.base_dir.mkdir(exist_ok=True)
        self.file_path = self.base_dir / 'core.json'
        self.files = {}
        self.history = []
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                data = json.loads(self.file_path.read_text(encoding='utf-8'))
                self.files = data.get('files', {})
                self.history = data.get('history', [])
            except:
                pass

    def save(self):
        data = {'files': self.files, 'history': self.history[-20:]}
        self.file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def update_file(self, filename: str, content: str):
        self.files[filename] = content
        self.save()

    def get_context(self) -> str:
        if not self.files:
            return 'No previous files in memory.'
        return '\n\n'.join([f'--- {f} ---\n{content[:700]}...' for f, content in list(self.files.items())[:2]])


class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url='https://api.groq.com/openai/v1') if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.memory = ProjectMemory()

    def _call(self, prompt: str, temperature: float = 0.3) -> str:
        if not self.client:
            return '# Groq API not configured'
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=temperature,
                max_tokens=1400
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f'# Error: {str(e)}'

    def iterative_loop(self, task: str, max_iterations: int = 2):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        context = self.memory.get_context()

        result = {'task': task, 'timestamp': timestamp, 'iterations': [], 'final_code': ''}

        current_code = '# Starting...'

        for i in range(1, max_iterations + 1):
            iter_log = {'iteration': i}

            # Planner
            plan = self._call(f"""You are the Planner. Task: {task}
Context: {context}
Give a short, clear, numbered plan.""", 0.2)
            iter_log['plan'] = plan

            # Coder
            current_code = self._call(f"""You are the Coder. 
{plan}

Write clean, production-ready Python code with good comments and examples.""", 0.3)
            iter_log['code'] = current_code

            # Reviewer
            review = self._call(f"""You are the Reviewer. Critically review this code briefly and list main issues:

{current_code}""", 0.2)
            iter_log['review'] = review

            # Optimizer
            current_code = self._call(f"""You are the Optimizer. Improve the code based on the review.
Output **ONLY** the final clean code. No explanations.""", 0.25)
            iter_log['optimized_code'] = current_code

            result['iterations'].append(iter_log)

        self.memory.update_file('latest_solution.py', current_code)
        self.memory.history.append({'task': task[:180], 'timestamp': timestamp})

        result['final_code'] = current_code

        return {
            'final_code': current_code,
            'full_result': result,
            'message': f"Grok's child v2.7 - Improved multi-agent [{timestamp}]"
        }


coding_system = CodingSystem()
