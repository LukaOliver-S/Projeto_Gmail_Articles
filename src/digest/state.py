import json
from pathlib import Path

class State:
    def __init__(self, state_file: str):
        self.state_file = Path(state_file)
        self.state = self._load_state()

    def _load_state(self):
        if self.state_file.exists():
                return set(json.loads(self.state_file.read_text(encoding = "utf-8")))
        return set()

    def save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.state), f, indent=2)
        
    
    def is_processed(self, email_id:str) -> bool:
        return email_id in self.state

    def mark_processed(self, email_id: str):
        self.state.add(email_id)
        self.save_state()