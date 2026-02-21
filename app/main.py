"""Minimal NiceGUI app scaffold for the crime network project."""

from __future__ import annotations

import sys
from pathlib import Path

from nicegui import ui

if __package__ is None or __package__ == '':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.formatting import format_inspector_rows
from app.graph_build import build_cytoscape_elements, build_networkx_graph
from app.graph_render import render_cytoscape
from app.io_excel import load_workbook
from app.validate import validate_data


@ui.page('/')
def index() -> None:
    """Render the phase-0 layout skeleton."""
    status_text = ''
    status_classes = 'text-sm '
    validation_messages: list[str] = []
    built_elements_status = ''
    networkx_status = ''
    elements: list[dict] | None = None
    selection_state = {'kind': 'none', 'data': {}}
    last_selection_signature = {'value': None}

    try:
        nodes_df, edges_df = load_workbook()
        validation_errors = validate_data(nodes_df, edges_df)

        if validation_errors:
            status_text = f'Validation errors: {len(validation_errors)}'
            status_classes += 'text-amber-300'
            validation_messages = [error['message'] for error in validation_errors[:5]]
        else:
            status_text = f'Loaded: {len(nodes_df)} nodes, {len(edges_df)} edges'
            status_classes += 'text-emerald-300'
            elements = build_cytoscape_elements(nodes_df, edges_df)
            node_elements = sum(1 for element in elements if 'label' in element['data'])
            edge_elements = sum(1 for element in elements if 'source' in element['data'])
            built_elements_status = f'Built: {node_elements} node elements, {edge_elements} edge elements'
            graph = build_networkx_graph(nodes_df, edges_df)
            networkx_status = f'NetworkX: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges'
    except (FileNotFoundError, ValueError) as error:
        status_text = f'Workbook error: {error}'
        status_classes += 'text-rose-300'

    with ui.row().classes('w-full h-screen no-wrap bg-slate-100'):
        with ui.column().classes('w-1/5 min-w-52 h-full bg-slate-900 text-white p-4 gap-3'):
            ui.label('Sidebar').classes('text-lg font-semibold')
            ui.label(status_text).classes(status_classes)
            if built_elements_status:
                ui.label(built_elements_status).classes('text-xs text-emerald-100')
            if networkx_status:
                ui.label(networkx_status).classes('text-xs text-emerald-100')
            for message in validation_messages:
                ui.label(f'• {message}').classes('text-xs text-amber-100')
            ui.separator().classes('bg-slate-700')
            ui.label('Placeholder controls').classes('text-sm text-slate-300')
            ui.button('Load workbook (coming soon)').props('outline')
            ui.button('Validate data (coming soon)').props('outline')
            ui.button('Export (coming soon)').props('outline')

        with ui.column().classes('w-3/5 h-full p-6 gap-4'):
            ui.label('Crime Network Viewer').classes('text-2xl font-bold text-slate-800')
            graph_card = ui.card().classes('w-full h-full bg-white')
            if elements is not None:
                render_cytoscape(
                    graph_card,
                    elements,
                    on_select=lambda payload: selection_state.update(
                        kind=payload.get('kind', 'none'),
                        data=payload.get('data', {}),
                    ),
                )
            else:
                with graph_card:
                    with ui.column().classes('w-full h-full items-center justify-center'):
                        ui.icon('hub').classes('text-6xl text-slate-400')
                        ui.label('Graph will render here').classes('text-lg text-slate-600')

        with ui.column().classes('w-1/5 min-w-52 h-full bg-white border-l border-slate-200 p-4 gap-3'):
            ui.label('Inspector').classes('text-lg font-semibold text-slate-800')
            ui.separator()
            inspector_placeholder = ui.label('Select a node/edge to inspect').classes('text-sm text-slate-500')
            inspector_kind = ui.label().classes('text-sm text-slate-700 font-medium')
            inspector_rows = ui.column().classes('w-full gap-1')

            def refresh_inspector() -> None:
                kind = selection_state.get('kind', 'none')
                selection_signature = (kind, repr(selection_state.get('data', {})))
                if selection_signature == last_selection_signature['value']:
                    return
                last_selection_signature['value'] = selection_signature

                if kind == 'none':
                    inspector_placeholder.set_visibility(True)
                    inspector_kind.set_text('')
                    inspector_rows.clear()
                    return

                inspector_placeholder.set_visibility(False)
                inspector_kind.set_text(f"Kind: {'Node' if kind == 'node' else 'Edge'}")

                rows = format_inspector_rows(kind, selection_state.get('data', {}))
                inspector_rows.clear()
                with inspector_rows:
                    for key, value in rows:
                        with ui.row().classes('w-full justify-between gap-2 text-sm'):
                            ui.label(key).classes('text-slate-500')
                            ui.label(value).classes('text-slate-800 text-right break-all')

            ui.timer(0.1, refresh_inspector)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Crime Network App (Phase 0)')
