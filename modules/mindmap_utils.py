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
    Generate a prompt for creating a Mermaid.js flowchart from text with inline styling.
    
    Args:
        text: The input text to convert to a flowchart
        
    Returns:
        str: Formatted prompt for the LLM
    """
    return f"""Convert the following text into a Mermaid.js flowchart that visually represents the main ideas and their relationships.
The flowchart should use INLINE STYLING for maximum compatibility. Follow these rules exactly:

1. Use this exact format for nodes:
   - Main concepts: style NODE fill:#e6f3ff,stroke:#66b3ff,color:#0066cc,stroke-width:2px
   - Details: style NODE fill:#fff9c4,stroke:#ffd54f,color:#5d4037,stroke-width:1.5px
   - Actions: style NODE fill:#e8f5e9,stroke:#81c784,color:#2e7d32,stroke-width:1.5px
   - Decisions: style NODE fill:#fce4ec,stroke:#f48fb1,color:#c2185b,stroke-width:1.5px,shape:rhombus
   - Results: style NODE fill:#f3e5f5,stroke:#ba68c8,color:#6a1b9a,stroke-width:1.5px

2. Start with: flowchart TD
3. Define all nodes first, then connections, then styles
4. Use simple node names (A, B, C, etc.)
5. Always enclose node text in double quotes
6. Use these arrow styles:
   - --> for main flows
   - -.-> for secondary relationships
   - ==> for important connections

Example of required format:
```mermaid
flowchart TD
    %% Define nodes
    A["Main Topic"]
    B["Key Point 1"]
    C["Key Point 2"]
    D["Supporting Detail"]
    E["Action Step"]
    F{{"Decision"}}
    G["Result A"]
    H["Result B"]
    
    %% Define connections
    A --> B
    A --> C
    B --> D
    B -->|leads to| E
    C --> F
    F -->|Yes| G
    F -->|No| H
    
    %% Apply styles
    style A fill:#e6f3ff,stroke:#66b3ff,color:#0066cc,stroke-width:2px
    style B fill:#e6f3ff,stroke:#66b3ff,color:#0066cc,stroke-width:2px
    style C fill:#e6f3ff,stroke:#66b3ff,color:#0066cc,stroke-width:2px
    style D fill:#fff9c4,stroke:#ffd54f,color:#5d4037,stroke-width:1.5px
    style E fill:#e8f5e9,stroke:#81c784,color:#2e7d32,stroke-width:1.5px
    style F fill:#fce4ec,stroke:#f48fb1,color:#c2185b,stroke-width:1.5px,shape:rhombus
    style G fill:#f3e5f5,stroke:#ba68c8,color:#6a1b9a,stroke-width:1.5px
    style H fill:#f3e5f5,stroke:#ba68c8,color:#6a1b9a,stroke-width:1.5px
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
