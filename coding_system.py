import os
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv(override=True)


class ProjectMemory:
    def __init__(self):
        self.base_dir = Path('project_memory')
        self.base_dir.mkdir(exist_ok=True)
        self.file_path = self.base_dir / 'core.json'
        self.files: Dict[str, str] = {}
        self.history: list = []
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
        data = {'files': self.files, 'history': self.history[-30:]}
        self.file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def update_file(self, filename: str, content: str, agent: str = "system"):
        self.files[filename] = content
        self.history.append({"timestamp": datetime.now().isoformat(), "agent": agent, "file": filename})
        self.save()

    def get_context(self) -> str:
        if not self.files:
            return "No previous code."
        recent = list(self.files.items())[:4]
        return '\n\n'.join([f'=== {fname} ===\n{content[:700]}...' for fname, content in recent])


class CodingSystem:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = OpenAI(api_key=api_key, base_url='https://api.groq.com/openai/v1') if api_key else None
        self.model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        self.memory = ProjectMemory()

    def _call(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1800) -> str:
        if not self.client:
            return "# API not configured"
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"# Error: {str(e)}"

    def iterative_loop(self, task: str):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
        context = self.memory.get_context()

        code_raw = self._call(f"""You are an expert Python developer.

TASK: {task}

MANDATORY REQUIREMENTS:
- Dataclass named exactly TradingPosition
- Fields: symbol: str, quantity: int, entry_price: float, exit_price: Optional[float] = None, is_long: bool = True
- Use __post_init__ for validation
- Include calculate_pnl() and calculate_percentage_return()
- Full type hints, detailed docstrings, example usage (long + short)
- ONLY standard library

Output ONLY the complete Python code.""", 0.1)

        self.memory.update_file('raw_code.py', code_raw, "Coder")

        review_raw = self._call(f"""You are the Reviewer.
Does this code fully meet the MANDATORY REQUIREMENTS?

Code:
{code_raw}

JSON only: {{"approved": true/false, "issues": []}}""", 0.1)

        self.memory.update_file('review.json', review_raw, "Reviewer")

        try:
            cleaned = review_raw.strip().strip('`json').strip('`').strip()
            review_data = json.loads(cleaned)
            approved = bool(review_data.get("approved", False))
        except:
            approved = False
            review_data = {"approved": False, "issues": ["Parse failed"]}

        final_code = code_raw if approved else self._call(f"""Fix to exactly match MANDATORY REQUIREMENTS.\nTask: {task}\nOutput ONLY code.""", 0.1)

        self.memory.update_file('final_solution.py', final_code, "Final")

        return {
            'final_code': final_code,
            'message': f"Grok's Baby v3.6.6 Stable - Strong Anchor [{timestamp}]",
            'review_approved': approved
        }


coding_system = CodingSystem()
