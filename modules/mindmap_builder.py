import uuid
import random
import json
from typing import Dict, List, Any, Optional, Tuple

def create_id() -> str:
    """Generate a unique ID for Excalidraw elements."""
    return str(uuid.uuid4())

def create_text_element(text: str, x: int, y: int, width: Optional[int] = None) -> Dict[str, Any]:
    """Create a text element for Excalidraw."""
    element_width = width if width is not None else max(100, len(text) * 8)
    return {
        "id": create_id(),
        "type": "text",
        "x": x,
        "y": y,
        "width": element_width,
        "height": 40,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "#fff",
        "fillStyle": "hachure",
        "strokeWidth": 1,
        "roughness": 1,
        "opacity": 100,
        "seed": random.randint(1, 999999),
        "text": text,
        "fontSize": 20,
        "fontFamily": 1,
        "textAlign": "left",
        "verticalAlign": "top",
        "baseline": 28,
        "containerId": None,
        "originalText": text,
        "version": 1,
        "versionNonce": random.randint(1, 999999),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
    }

def create_arrow(start_id: str, end_id: str) -> Dict[str, Any]:
    """Create an arrow connecting two elements in Excalidraw."""
    return {
        "id": create_id(),
        "type": "arrow",
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0,
        "angle": 0,
        "strokeColor": "#1e1e1e",
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 2,
        "roughness": 1,
        "opacity": 100,
        "points": [[0, 0], [1, 1]],
        "startBinding": {
            "elementId": start_id,
            "focus": 0.5,
            "gap": 1,
        },
        "endBinding": {
            "elementId": end_id,
            "focus": 0.5,
            "gap": 1,
        },
        "startArrowhead": None,
        "endArrowhead": "arrow",
        "seed": random.randint(1, 999999),
        "version": 1,
        "versionNonce": random.randint(1, 999999),
        "isDeleted": False,
        "groupIds": [],
        "boundElements": [],
    }

def calculate_text_dimensions(text: str, font_size: int = 20) -> Dict[str, int]:
    """Estimate text dimensions based on character count and font size."""
    avg_char_width = font_size * 0.6  # Rough estimate
    lines = text.split('\n')
    max_line_length = max(len(line) for line in lines) if lines else 0
    return {
        'width': int(max_line_length * avg_char_width) + 40,  # Add padding
        'height': len(lines) * (font_size + 4) + 20,  # Add padding between lines
    }

def build_mind_map(
    node: Dict[str, Any],
    x: int = 100,
    y: int = 100,
    level: int = 0,
    spacing_y: int = 120,
    spacing_x: int = 300
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Recursively build a mind map from a hierarchical structure.
    
    Args:
        node: The current node in the mind map
        x: Current x position
        y: Current y position
        level: Current depth level in the hierarchy
        spacing_y: Vertical spacing between nodes
        spacing_x: Horizontal spacing between levels
        
    Returns:
        Tuple of (elements, node_id) where elements is a list of Excalidraw elements
        and node_id is the ID of the current node.
    """
    elements = []
    
    # Create the current node
    node_text = node.get('text', 'Untitled')
    text_dims = calculate_text_dimensions(node_text)
    
    node_elem = create_text_element(
        node_text,
        x=x,
        y=y - text_dims['height'] // 2,  # Center vertically
        width=text_dims['width']
    )
    elements.append(node_elem)
    
    # Process children if they exist
    if 'children' in node and node['children']:
        children = node['children']
        total_height = (len(children) - 1) * spacing_y
        start_y = y - total_height // 2  # Center children vertically
        
        for i, child in enumerate(children):
            child_y = start_y + i * spacing_y
            child_elements, child_id = build_mind_map(
                child,
                x + spacing_x,
                child_y,
                level + 1,
                spacing_y,
                spacing_x
            )
            elements.extend(child_elements)
            
            # Create an arrow from parent to child
            arrow = create_arrow(node_elem['id'], child_id)
            elements.append(arrow)
    
    return elements, node_elem['id']

def create_excalidraw_data(mindmap_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a mind map structure to Excalidraw data format.
    
    Args:
        mindmap_data: Dictionary containing the mind map structure
        
    Returns:
        Dictionary with Excalidraw data
    """
    elements, _ = build_mind_map(mindmap_data)
    
    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {
            "gridSize": 20,
            "viewBackgroundColor": "#ffffff",
            "currentItemStrokeColor": "#1e1e1e",
            "currentItemBackgroundColor": "#fff",
            "currentItemFillStyle": "hachure",
            "currentItemStrokeWidth": 1,
            "currentItemRoughness": 1,
            "currentItemOpacity": 100,
            "currentItemFontFamily": 1,
            "currentItemFontSize": 20,
            "currentItemTextAlign": "left",
            "currentItemStrokeSharpness": "sharp",
            "currentItemStartArrowhead": None,
            "currentItemEndArrowhead": "arrow",
            "currentItemLinearStrokeSharpness": "round",
            "theme": "light",
            "viewModeEnabled": False,
        },
        "files": {}
    }

def get_excalidraw_html(excalidraw_data: Dict[str, Any]) -> str:
    """
    Generate HTML to embed an Excalidraw drawing.
    
    Args:
        excalidraw_data: Excalidraw data to display
        
    Returns:
        HTML string for embedding
    """
    excalidraw_json = json.dumps(excalidraw_data)
    
    # Escape the JSON data for JavaScript
    escaped_json = json.dumps(excalidraw_data)
    
    # Create a data URL with the Excalidraw HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Mind Map</title>
        <script src="https://unpkg.com/@excalidraw/excalidraw@0.16.3/dist/excalidraw.min.js"></script>
        <style>
            body, html, #excalidraw {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }}
            #status {{
                position: fixed;
                top: 10px;
                left: 50%;
                transform: translateX(-50%);
                padding: 10px 20px;
                background: rgba(255,255,255,0.9);
                border: 1px solid #ccc;
                border-radius: 4px;
                z-index: 1000;
                font-family: sans-serif;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div id="status">Loading mind map...</div>
        <div id="excalidraw" style="width: 100%; height: 100%;"></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                try {{
                    console.log('Initializing Excalidraw...');
                    const excalidrawData = {escaped_json};
                    
                    function initExcalidraw() {{
                        console.log('Creating Excalidraw instance...');
                        console.log('Elements:', excalidrawData.elements);
                        
                        const {{ Excalidraw, ExcalidrawCore }} = window.ExcalidrawLib;
                        const excalidrawElement = document.getElementById('excalidraw');
                        
                        try {{
                            const excalidrawInstance = new ExcalidrawCore.Excalidraw({{
                                target: excalidrawElement,
                                initialData: {{
                                    elements: Array.isArray(excalidrawData.elements) ? excalidrawData.elements : [],
                                    appState: {{
                                        ...(excalidrawData.appState || {{}}),
                                        scrollToContent: true,
                                        viewBackgroundColor: '#ffffff',
                                        theme: 'light'
                                    }},
                                    files: {{}}
                                }},
                                UIOptions: {{
                                    canvasActions: {{
                                        loadScene: false,
                                        saveToActiveFile: false,
                                        export: false,
                                        clearCanvas: false,
                                        theme: false,
                                        saveAsImage: false
                                    }}
                                }},
                                viewModeEnabled: true,
                                handleKeyboardGlobally: false,
                                width: '100%',
                                height: '100%',
                            }});
                            
                            // Update status
                            const status = document.getElementById('status');
                            status.textContent = 'Mind map loaded';
                            status.style.background = '#e6f7e6';
                            status.style.borderColor = '#4CAF50';
                            
                            // Auto-hide status after delay
                            setTimeout(() => {{
                                status.style.opacity = '0';
                                setTimeout(() => status.style.display = 'none', 300);
                            }}, 2000);
                            
                            // Handle window resize
                            const resizeObserver = new ResizeObserver(() => {{
                                excalidrawInstance.refresh();
                            }});
                            
                            resizeObserver.observe(excalidrawElement);
                            
                            // Initial refresh
                            setTimeout(() => {{
                                excalidrawInstance.refresh();
                                excalidrawInstance.scrollToContent({{}});
                            }}, 100);
                            
                            // Notify parent window when ready
                            if (window.parent) {{
                                window.parent.postMessage({{ type: 'excalidrawReady' }}, '*');
                            }}
                            
                        }} catch (error) {{
                            console.error('Error creating Excalidraw instance:', error);
                            const status = document.getElementById('status');
                            status.textContent = 'Error: ' + error.message;
                            status.style.background = '#ffebee';
                            status.style.borderColor = '#f44336';
                        }}
                    }}
                    
                    // Initialize when Excalidraw is loaded
                    if (window.ExcalidrawLib) {{
                        initExcalidraw();
                    }} else {{
                        const script = document.createElement('script');
                        script.src = 'https://unpkg.com/@excalidraw/excalidraw@0.16.3/dist/excalidraw.min.js';
                        script.onload = initExcalidraw;
                        document.head.appendChild(script);
                    }}
                    
                }} catch (error) {{
                    console.error('Error initializing mind map:', error);
                    document.body.innerHTML = `
                        <div style="
                            padding: 20px; 
                            color: #721c24; 
                            background-color: #f8d7da; 
                            border: 1px solid #f5c6cb;
                            border-radius: 4px;
                            margin: 20px;
                            font-family: sans-serif;
                        ">
                            <h3>Error Loading Mind Map</h3>
                            <p>${{error.message || 'Unknown error occurred'}}</p>
                            <pre style="white-space: pre-wrap; background: white; padding: 10px; border-radius: 4px;">${{error.stack || ''}}</pre>
                        </div>`;
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    # Create a data URL for the iframe
    data_url = f"data:text/html;charset=utf-8,{html_content}"
    
    # Return an iframe that loads the content
    return f"""
    <iframe 
        srcdoc='{data_url.replace("'", "&apos;")}'
        style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 4px;"
        frameborder="0"
        allowfullscreen="true"
        sandbox="allow-same-origin allow-scripts allow-popups allow-forms"
    ></iframe>
    """
