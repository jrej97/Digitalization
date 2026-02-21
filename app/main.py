"""Minimal NiceGUI app scaffold for the crime network project."""

from nicegui import ui

from app.graph_build import build_cytoscape_elements
from app.io_excel import load_workbook
from app.validate import validate_data


@ui.page('/')
def index() -> None:
    """Render the phase-0 layout skeleton."""
    status_text = ''
    status_classes = 'text-sm '
    validation_messages: list[str] = []
    built_elements_status = ''

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
    except (FileNotFoundError, ValueError) as error:
        status_text = f'Workbook error: {error}'
        status_classes += 'text-rose-300'

    with ui.row().classes('w-full h-screen no-wrap bg-slate-100'):
        with ui.column().classes('w-1/5 min-w-52 h-full bg-slate-900 text-white p-4 gap-3'):
            ui.label('Sidebar').classes('text-lg font-semibold')
            ui.label(status_text).classes(status_classes)
            if built_elements_status:
                ui.label(built_elements_status).classes('text-xs text-emerald-100')
            for message in validation_messages:
                ui.label(f'• {message}').classes('text-xs text-amber-100')
            ui.separator().classes('bg-slate-700')
            ui.label('Placeholder controls').classes('text-sm text-slate-300')
            ui.button('Load workbook (coming soon)').props('outline')
            ui.button('Validate data (coming soon)').props('outline')
            ui.button('Export (coming soon)').props('outline')

        with ui.column().classes('w-3/5 h-full p-6 gap-4'):
            ui.label('Crime Network Viewer').classes('text-2xl font-bold text-slate-800')
            with ui.card().classes('w-full h-full items-center justify-center bg-white'):
                ui.icon('hub').classes('text-6xl text-slate-400')
                ui.label('Graph will render here').classes('text-lg text-slate-600')

        with ui.column().classes('w-1/5 min-w-52 h-full bg-white border-l border-slate-200 p-4 gap-3'):
            ui.label('Inspector').classes('text-lg font-semibold text-slate-800')
            ui.separator()
            ui.label('Select a node/edge to inspect').classes('text-sm text-slate-500')


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Crime Network App (Phase 0)')
