"""Cytoscape renderer for the NiceGUI center panel."""

from __future__ import annotations

import json
from uuid import uuid4

from nicegui import ui

_CYTOSCAPE_CDN_INJECTED = False
_CYTOSCAPE_CDN_URL = 'https://unpkg.com/cytoscape@3.29.2/dist/cytoscape.min.js'


def _ensure_cytoscape_cdn() -> None:
    """Inject Cytoscape.js into the page head once."""
    global _CYTOSCAPE_CDN_INJECTED
    if _CYTOSCAPE_CDN_INJECTED:
        return

    ui.add_head_html(
        (
            '<script>'
            "if (!window.__cytoscapeScriptRequested) {"
            '  window.__cytoscapeScriptRequested = true;'
            "  const script = document.createElement('script');"
            f"  script.src = '{_CYTOSCAPE_CDN_URL}';"
            '  script.async = true;'
            '  document.head.appendChild(script);'
            '}'
            '</script>'
        )
    )
    _CYTOSCAPE_CDN_INJECTED = True


def render_cytoscape(container, elements: list[dict], *, height: str = '75vh') -> None:
    """Render Cytoscape graph inside the given NiceGUI container."""
    _ensure_cytoscape_cdn()

    container_id = f'cy-{uuid4().hex}'
    serialized_elements = json.dumps(elements)

    with container:
        ui.html(
            f'<div id="{container_id}" style="width: 100%; height: {height}; min-height: 420px;"></div>'
        )

    ui.run_javascript(
        f"""
        (() => {{
          const targetId = {json.dumps(container_id)};
          const graphElements = {serialized_elements};

          function initCytoscape() {{
            const host = document.getElementById(targetId);
            if (!host || !window.cytoscape) return false;

            window.cytoscape({{
              container: host,
              elements: graphElements,
              style: [
                {{
                  selector: 'node',
                  style: {{
                    'background-color': '#ffffff',
                    'border-color': '#cbd5e1',
                    'border-width': 1.5,
                    'width': 40,
                    'height': 40,
                    'shape': 'ellipse',
                    'label': 'data(label)',
                    'color': '#334155',
                    'font-size': 11,
                    'text-valign': 'bottom',
                    'text-halign': 'center',
                    'text-margin-y': 9,
                    'text-wrap': 'wrap',
                    'text-max-width': 90
                  }}
                }},
                {{
                  selector: 'edge',
                  style: {{
                    'line-color': '#cbd5e1',
                    'width': 1.2,
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'none',
                    'source-arrow-shape': 'none'
                  }}
                }}
              ],
              layout: {{
                name: 'cose',
                animate: false,
                fit: true,
                padding: 36,
                nodeRepulsion: 400000,
                idealEdgeLength: 110
              }}
            }});
            return true;
          }}

          if (!initCytoscape()) {{
            let attempts = 0;
            const maxAttempts = 50;
            const timer = setInterval(() => {{
              attempts += 1;
              if (initCytoscape() || attempts >= maxAttempts) {{
                clearInterval(timer);
              }}
            }}, 100);
          }}
        }})();
        """
    )
