import re


class PageBodyBuilder:
    def __init__(self):
       self.blocks = []

    def heading(self, text: str, level: int = 1):
        """Add a heading block to the page body."""
        self.blocks.append({
            "object": "block",
            "type": f"heading_{level}",
            f"heading_{level}": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        })
        return self

    def paragraph(self, text: str):
        """Add a paragraph block to the page body."""
        self.blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            }
        })
        return self

    def bulleted_list_item(self, items: list[str]):
        """Add a bulleted list item block to the page body."""
        for item in items:
            self.blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": str(item)}}]
                }
            })
        return self

    def section(self, title:str = None,paragraph:str = None,bulleted_list:list[str] = None,diagram_code:str = None):
        """Add a section with a heading, paragraph, optional bulleted list, and optional Mermaid diagram."""
        if not (paragraph or bulleted_list or diagram_code):
            return self    
        if paragraph:
             self.paragraph(paragraph)
        if bulleted_list:
            self.bulleted_list_item(bulleted_list)
        if diagram_code:
            self.mermaid_diagram(title,diagram_code)
        return self
        
    def mermaid_diagram(self, title:str, source: str):
        """Add a Mermaid diagram block to the page body."""
        self.heading(title, level=2)
        self.blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": source}}],
                "language": "mermaid"
            }
        })
        return self

    @staticmethod
    def pipeline_to_mermaid(steps: list[str],max_char:int = 100) -> str:
        """Convert a list of steps into a Mermaid flowchart string."""
        if not steps:
            return ""
        mermaid_lines = ["flowchart TD"]
        for i, step in enumerate(steps):
            label = step.replace('"',"'").replace("\n"," ").replace("[", "(").replace("]", ")")
            label = label[:max_char]

            step_id = f"Step{i+1}"
            mermaid_lines.append(f'{step_id}["{label}"]')
            if i > 0:
                prev_step_id = f"Step{i}"
                mermaid_lines.append(f'{prev_step_id} --> {step_id}')
        return "\n".join(mermaid_lines)

    def build(self) -> list:
        """Return the list of blocks representing the page body."""
        return self.blocks