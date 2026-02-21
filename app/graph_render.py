"""Cytoscape renderer for the NiceGUI center panel."""

from __future__ import annotations

import json
from collections.abc import Callable
from uuid import uuid4

from fastapi import Body
from nicegui import app, ui

_CYTOSCAPE_CDN_INJECTED = False
_CYTOSCAPE_CDN_URL = 'https://unpkg.com/cytoscape@3.29.2/dist/cytoscape.min.js'
_SELECTION_ENDPOINT_REGISTERED = False
_SELECTION_CALLBACKS: dict[str, Callable[[dict], None]] = {}


def _ensure_selection_endpoint() -> None:
    """Register an API endpoint that receives Cytoscape selection payloads from JS."""
    global _SELECTION_ENDPOINT_REGISTERED
    if _SELECTION_ENDPOINT_REGISTERED:
        return

    @app.post('/api/selection/{selection_id}')
    async def _receive_selection(selection_id: str, payload: dict = Body(default=None)) -> dict[str, str]:
        callback = _SELECTION_CALLBACKS.get(selection_id)
        if callback is None:
            return {'status': 'ignored'}

        safe_payload = payload if isinstance(payload, dict) else {}
        kind = safe_payload.get('kind')
        if kind not in {'node', 'edge', 'none'}:
            kind = 'none'

        data = safe_payload.get('data')
        if not isinstance(data, dict):
            data = {}

        callback({'kind': kind, 'data': data})
        return {'status': 'ok'}

    _SELECTION_ENDPOINT_REGISTERED = True


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


def render_cytoscape(container, elements: list[dict], *, height: str = '75vh', on_select=None) -> None:
    """Render Cytoscape graph inside the given NiceGUI container."""
    _ensure_cytoscape_cdn()
    if on_select is not None:
        _ensure_selection_endpoint()

    container_id = f'cy-{uuid4().hex}'
    serialized_elements = json.dumps(elements)
    selection_id = uuid4().hex if on_select is not None else None
    if selection_id is not None:
        _SELECTION_CALLBACKS[selection_id] = on_select

    with container:
        ui.html(
            f'<div id="{container_id}" style="width: 100%; height: {height}; min-height: 420px;"></div>'
        )

    ui.run_javascript(
        f"""
        (() => {{
          const targetId = {json.dumps(container_id)};
          const graphElements = {serialized_elements};

          function sendSelection(kind, data) {{
            const selectionId = {json.dumps(selection_id)};
            if (!selectionId) return;
            fetch(`/api/selection/${{selectionId}}`, {{
              method: 'POST',
              headers: {{ 'Content-Type': 'application/json' }},
              body: JSON.stringify({{ kind, data }}),
            }}).catch(() => {{}});
          }}

          function initCytoscape() {{
            const host = document.getElementById(targetId);
            if (!host || !window.cytoscape) return false;

            const cy = window.cytoscape({{
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

            cy.on('tap', 'node', (event) => {{
              sendSelection('node', event.target.data());
            }});

            cy.on('tap', 'edge', (event) => {{
              sendSelection('edge', event.target.data());
            }});

            cy.on('tap', (event) => {{
              if (event.target === cy) {{
                sendSelection('none', {{}});
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
