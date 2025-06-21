"""
Utility functions for generating and displaying mind maps.
"""
import re
import json
from typing import Dict, Any, Tuple, Optional

def generate_mindmap_prompt(text: str) -> str:
    """
    Generate a prompt for the LLM to create a mind map from text.
    
    Args:
        text: The input text to convert to a mind map
        
    Returns:
        str: Formatted prompt for the LLM
    """
    return f"""Convert the following text into a hierarchical mind map structure in JSON format.
The JSON should have a hierarchical structure with 'text' and 'children' fields.
Each node should have a 'text' field that summarizes the concept.
The root node should represent the main topic.

Example output format:
{{
    "text": "Main Topic",
    "children": [
        {{
            "text": "Subtopic 1",
            "children": [
                {{"text": "Detail 1"}},
                {{"text": "Detail 2"}}
            ]
        }},
        {{
            "text": "Subtopic 2",
            "children": [
                {{"text": "Detail 3"}},
                {{"text": "Detail 4"}}
            ]
        }}
    ]
}}

Text to convert to mind map:
{text}"""

def generate_flowchart_prompt(text: str) -> str:
    """
    Generate a prompt for creating a Mermaid.js flowchart from text.
    
    Args:
        text: The input text to convert to a flowchart
        
    Returns:
        str: Formatted prompt for the LLM
    """
    return f"""Convert the following text into a Mermaid.js flowchart that visually represents the main ideas and their relationships.
The flowchart should be structured with clear nodes and logical connections.

Follow these guidelines:
1. Start with 'flowchart TD' (Top-Down direction)
2. Use square brackets [] for regular nodes
3. Use double curly brackets {{}} for decision points
4. Use arrows (-->) to connect nodes
5. Use text on arrows to describe relationships (e.g., A -->|leads to| B)
6. Keep node labels concise but meaningful
7. Group related concepts together
8. Highlight key points or main ideas
9. Quote node labels with spaces/special characters.

Example:
```mermaid
flowchart TD
    A["Main Topic"] --> B["Subtopic 1"]
    A --> C["Subtopic 2"]
    B --> D["Point A"]
    B --> E["Point B"]
    C -->|leads to| F["Conclusion"]
```

Text to convert to flowchart:
{text}"""

def parse_llm_response(response: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Parse the LLM response to extract JSON and Mermaid code.
    
    Args:
        response: Raw response from the LLM
        
    Returns:
        Tuple containing (mermaid_code, mind_map_data)
    """
    mermaid_code = None
    mind_map_data = None
    
    # Try to extract Mermaid code
    mermaid_match = re.search(r'```(?:mermaid)?\n?(.*?)\n?```', response, re.DOTALL)
    if mermaid_match:
        mermaid_code = mermaid_match.group(1).strip()
        if not mermaid_code.startswith('flowchart'):
            mermaid_code = 'flowchart TD\n' + mermaid_code
    
    # Try to extract JSON
    json_match = re.search(r'```(?:json\n)?(.*?)\n?```', response, re.DOTALL)
    if json_match:
        try:
            mind_map_data = json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    return mermaid_code, mind_map_data
