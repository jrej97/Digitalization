"""Minimal NiceGUI app scaffold for the crime network project."""

from nicegui import ui


@ui.page('/')
def index() -> None:
    """Render the phase-0 layout skeleton."""
    with ui.row().classes('w-full h-screen no-wrap bg-slate-100'):
        with ui.column().classes('w-1/5 min-w-52 h-full bg-slate-900 text-white p-4 gap-3'):
            ui.label('Sidebar').classes('text-lg font-semibold')
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
