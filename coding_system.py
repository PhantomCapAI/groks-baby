import subprocess
import json
import difflib
from pathlib import Path
from typing import Dict, List

class Agent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

class CodingSystem:
    def __init__(self, repo_root: str = '.'):
        self.repo_root = Path(repo_root)
        self.memory_short: List[Dict] = []
        self.max_iterations = 6

    def _call_agent(self, name: str, data: Dict) -> str:
        # TODO: Replace this with real LLM call later
        return json.dumps({'result': f'Stub response from {name}'})

    def iterative_loop(self, task: str):
        self.memory_short.clear()
        self.memory_short.append({'step': 'start', 'task': task})
        return f'Diff would go here for task: {task[:100]}...'
