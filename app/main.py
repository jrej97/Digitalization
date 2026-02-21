"""Minimal NiceGUI app scaffold for the crime network project."""

from __future__ import annotations

import sys
from pathlib import Path

from nicegui import ui

if __package__ is None or __package__ == '':
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.crud_nodes import NODE_TYPE_OPTIONS, can_delete_node, is_unique_node_id
from app.formatting import format_inspector_rows
from app.graph_build import build_cytoscape_elements, build_networkx_graph
from app.graph_render import render_cytoscape
from app.io_excel import load_workbook
from app.validate import validate_data


@ui.page('/')
def index() -> None:
    """Render the phase-0 layout skeleton."""
    state = {
        'nodes_df': None,
        'edges_df': None,
        'validation_messages': [],
        'status_text': '',
        'status_classes': 'text-sm ',
        'built_elements_status': '',
        'networkx_status': '',
        'elements': None,
    }
    selection_state = {'kind': 'none', 'data': {}}
    last_selection_signature = {'value': None}

    def refresh_graph_state() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            return

        errors = validate_data(nodes_df, edges_df)
        state['validation_messages'] = [error['message'] for error in errors[:5]]
        if errors:
            state['status_text'] = f'Validation errors: {len(errors)}'
            state['status_classes'] = 'text-sm text-amber-300'
            state['built_elements_status'] = ''
            state['networkx_status'] = ''
            state['elements'] = None
            return

        state['status_text'] = f"Loaded: {len(nodes_df)} nodes, {len(edges_df)} edges"
        state['status_classes'] = 'text-sm text-emerald-300'
        elements = build_cytoscape_elements(nodes_df, edges_df)
        state['elements'] = elements
        node_elements = sum(1 for element in elements if 'label' in element['data'])
        edge_elements = sum(1 for element in elements if 'source' in element['data'])
        state['built_elements_status'] = f'Built: {node_elements} node elements, {edge_elements} edge elements'
        graph = build_networkx_graph(nodes_df, edges_df)
        state['networkx_status'] = f'NetworkX: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges'

    try:
        nodes_df, edges_df = load_workbook()
        state['nodes_df'] = nodes_df
        state['edges_df'] = edges_df
        refresh_graph_state()
    except (FileNotFoundError, ValueError) as error:
        state['status_text'] = f'Workbook error: {error}'
        state['status_classes'] = 'text-sm text-rose-300'

    with ui.row().classes('w-full h-screen no-wrap bg-slate-100'):
        with ui.column().classes('w-1/5 min-w-52 h-full bg-slate-900 text-white p-4 gap-3'):
            ui.label('Sidebar').classes('text-lg font-semibold')
            status_label = ui.label(state['status_text']).classes(state['status_classes'])
            built_label = ui.label(state['built_elements_status']).classes('text-xs text-emerald-100')
            networkx_label = ui.label(state['networkx_status']).classes('text-xs text-emerald-100')
            validation_list = ui.column().classes('w-full gap-1')

            ui.separator().classes('bg-slate-700')
            ui.label('Navigation').classes('text-sm text-slate-300')
            manage_button = ui.button('Manage Nodes').props('outline')
            back_button = ui.button('Back to Graph').props('outline')

            def refresh_sidebar_status() -> None:
                status_label.set_text(state['status_text'])
                status_label.classes(replace=state['status_classes'])
                built_label.set_text(state['built_elements_status'])
                built_label.set_visibility(bool(state['built_elements_status']))
                networkx_label.set_text(state['networkx_status'])
                networkx_label.set_visibility(bool(state['networkx_status']))
                validation_list.clear()
                with validation_list:
                    for message in state['validation_messages']:
                        ui.label(f'• {message}').classes('text-xs text-amber-100')

        with ui.column().classes('w-3/5 h-full p-6 gap-4') as center_column:
            ui.label('Crime Network Viewer').classes('text-2xl font-bold text-slate-800')
            view_container = ui.column().classes('w-full h-full')

        with ui.column().classes('w-1/5 min-w-52 h-full bg-white border-l border-slate-200 p-4 gap-3'):
            ui.label('Inspector').classes('text-lg font-semibold text-slate-800')
            ui.separator()
            inspector_placeholder = ui.label('Select a node/edge to inspect').classes('text-sm text-slate-500')
            inspector_kind = ui.label().classes('text-sm text-slate-700 font-medium')
            inspector_rows = ui.column().classes('w-full gap-1')

    nodes_table = {'element': None}

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

    def clear_selection() -> None:
        selection_state.update(kind='none', data={})
        last_selection_signature['value'] = None
        refresh_inspector()

    def render_graph_view() -> None:
        view_container.clear()
        with view_container:
            graph_card = ui.card().classes('w-full h-full bg-white')
            if state['elements'] is not None:
                render_cytoscape(
                    graph_card,
                    state['elements'],
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

    def current_nodes_rows() -> list[dict]:
        nodes_df = state['nodes_df']
        if nodes_df is None:
            return []
        expected_cols = ['id', 'label', 'type', 'description']
        available_cols = [col for col in expected_cols if col in nodes_df.columns]
        return nodes_df[available_cols].fillna('').to_dict('records')

    def refresh_nodes_table() -> None:
        table = nodes_table['element']
        if table is None:
            return
        table.rows = current_nodes_rows()
        table.update()

    selected_node = {'id': None}

    def open_node_dialog(mode: str) -> None:
        editing_id = selected_node['id']
        if mode == 'edit' and not editing_id:
            ui.notify('Select a node row first', type='warning')
            return

        nodes_df = state['nodes_df']
        if nodes_df is None:
            ui.notify('Nodes are not available', type='negative')
            return

        initial = {'id': '', 'label': '', 'type': NODE_TYPE_OPTIONS[0], 'description': ''}
        editing_index = None
        if mode == 'edit':
            matches = nodes_df.index[nodes_df['id'].astype(str).eq(str(editing_id))].tolist()
            if not matches:
                ui.notify('Selected node no longer exists', type='warning')
                return
            editing_index = matches[0]
            row = nodes_df.loc[editing_index]
            initial = {
                'id': str(row.get('id', '')),
                'label': str(row.get('label', '')),
                'type': str(row.get('type', NODE_TYPE_OPTIONS[0])),
                'description': str(row.get('description', '')),
            }

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Node' if mode == 'add' else 'Edit Node').classes('text-lg font-semibold')
            node_id = ui.input('id', value=initial['id'])
            label = ui.input('label', value=initial['label'])
            node_type = ui.select(options=NODE_TYPE_OPTIONS, label='type', value=initial['type'])
            description = ui.textarea('description', value=initial['description'])
            error_label = ui.label().classes('text-sm text-rose-600')

            def save_node() -> None:
                id_value = node_id.value.strip() if isinstance(node_id.value, str) else ''
                label_value = label.value.strip() if isinstance(label.value, str) else ''
                type_value = node_type.value if isinstance(node_type.value, str) else ''
                description_value = description.value.strip() if isinstance(description.value, str) else ''

                if not id_value or not label_value or not type_value:
                    error_label.set_text('id, label, and type are required')
                    return

                if not is_unique_node_id(nodes_df, id_value, exclude_index=editing_index):
                    error_label.set_text(f"Node id '{id_value}' is already in use")
                    return

                new_row = {
                    'id': id_value,
                    'label': label_value,
                    'type': type_value,
                    'description': description_value,
                }

                if mode == 'add':
                    state['nodes_df'] = nodes_df.loc[:, nodes_df.columns].copy()
                    state['nodes_df'].loc[len(state['nodes_df'])] = new_row
                    selected_node['id'] = id_value
                else:
                    state['nodes_df'] = nodes_df.copy()
                    for key, value in new_row.items():
                        state['nodes_df'].at[editing_index, key] = value
                    selected_node['id'] = id_value

                refresh_graph_state()
                refresh_sidebar_status()
                refresh_nodes_table()
                render_graph_view()
                clear_selection()
                dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Save', on_click=save_node)

        dialog.open()

    def delete_selected_node() -> None:
        node_id = selected_node['id']
        if not node_id:
            ui.notify('Select a node row first', type='warning')
            return

        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            ui.notify('Data is not available', type='negative')
            return

        allowed, ref_count = can_delete_node(edges_df, str(node_id))
        if not allowed:
            ui.notify(
                f"Cannot delete node '{node_id}': referenced by {ref_count} edge(s)",
                type='warning',
            )
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Delete node?').classes('text-lg font-semibold')
            ui.label(f"Are you sure you want to delete node '{node_id}'?")

            def confirm_delete() -> None:
                state['nodes_df'] = nodes_df[~nodes_df['id'].astype(str).eq(str(node_id))].reset_index(drop=True)
                selected_node['id'] = None
                refresh_graph_state()
                refresh_sidebar_status()
                refresh_nodes_table()
                render_graph_view()
                clear_selection()
                dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Delete', on_click=confirm_delete).props('color=negative')

        dialog.open()

    def render_manage_nodes_view() -> None:
        view_container.clear()
        with view_container:
            with ui.card().classes('w-full h-full bg-white'):
                ui.label('Manage Nodes').classes('text-xl font-semibold text-slate-800')
                ui.label('Add, edit, or delete nodes in memory (not saved to Excel yet).').classes(
                    'text-sm text-slate-500'
                )
                columns = [
                    {'name': 'id', 'label': 'id', 'field': 'id', 'required': True, 'align': 'left'},
                    {'name': 'label', 'label': 'label', 'field': 'label', 'align': 'left'},
                    {'name': 'type', 'label': 'type', 'field': 'type', 'align': 'left'},
                    {'name': 'description', 'label': 'description', 'field': 'description', 'align': 'left'},
                ]
                nodes_table['element'] = ui.table(
                    columns=columns,
                    rows=current_nodes_rows(),
                    row_key='id',
                    selection='single',
                    pagination={'rowsPerPage': 10},
                ).classes('w-full')

                def on_row_select(event) -> None:
                    row = event.args.get('added', [])
                    if row:
                        selected_node['id'] = row[0].get('id')

                nodes_table['element'].on('selection', on_row_select)

                with ui.row().classes('gap-2 mt-2'):
                    ui.button('Add', on_click=lambda: open_node_dialog('add'))
                    ui.button('Edit', on_click=lambda: open_node_dialog('edit')).props('outline')
                    ui.button('Delete', on_click=delete_selected_node).props('outline color=negative')

    render_graph_view()
    refresh_sidebar_status()

    manage_button.on_click(render_manage_nodes_view)
    back_button.on_click(render_graph_view)

    ui.timer(0.1, refresh_inspector)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title='Crime Network App (Phase 0)')
