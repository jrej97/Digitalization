"""Minimal NiceGUI app scaffold for the crime network project."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nicegui import ui

from app.config import get_default_data_path
from app.crud_edges import can_add_or_edit_edge
from app.crud_nodes import NODE_TYPE_OPTIONS, can_delete_node, is_unique_node_id
from app.export import export_csv, export_gexf, export_summary
from app.filtering import (
    DEFAULT_NODE_TYPE_FILTER,
    DEFAULT_RELATIONSHIP_FILTER,
    DEFAULT_SEARCH_FILTER,
    apply_filters,
)
from app.graph_build import build_cytoscape_elements, build_networkx_graph
from app.graph_render import render_cytoscape
from app.io_excel import load_workbook, save_workbook
from app.provenance import ensure_metadata_columns, is_valid_optional_date, parse_optional_confidence
from app.sample_data import create_sample_workbook
from app.state_guardrails import is_dirty, mark_clean, mark_dirty
from app.validate import validate_data


@ui.page('/')
def index() -> None:
    """Render the app layout."""
    state: dict[str, Any] = {
        'nodes_df': None,
        'edges_df': None,
        'validation_errors': [],
        'status_text': '',
        'status_classes': 'text-sm',
        'built_elements_status': '',
        'networkx_status': '',
        'elements': None,
        'nx_graph': None,
        'filter_type': DEFAULT_NODE_TYPE_FILTER,
        'filter_relationship_type': DEFAULT_RELATIONSHIP_FILTER,
        'filter_search': DEFAULT_SEARCH_FILTER,
        'active_view': 'graph',
        'render_loading': False,
    }
    selection_state = {'kind': 'none', 'data': {}}
    last_selection_signature = {'value': None}
    filter_debounce = {'token': 0}
    workbook_path = Path(get_default_data_path())
    workbook_label = str(workbook_path)

    def has_validation_errors() -> bool:
        return bool(state['validation_errors'])

    def format_error(error: dict[str, Any]) -> str:
        where = str(error.get('where', '') or '').strip()
        row = error.get('row')
        parts = []
        if where:
            parts.append(where)
        if row not in (None, ''):
            parts.append(f'row={row}')
        prefix = f"[{', '.join(parts)}] " if parts else ''
        return prefix + str(error.get('message', 'Unknown validation error'))

    def refresh_graph_state() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            return

        errors = validate_data(nodes_df, edges_df)
        state['validation_errors'] = errors
        if errors:
            state['status_text'] = f'Validation errors: {len(errors)}'
            state['status_classes'] = 'text-sm text-amber-300'
            state['built_elements_status'] = ''
            state['networkx_status'] = ''
            state['elements'] = None
            state['nx_graph'] = None
            return

        state['status_text'] = f"Loaded: {len(nodes_df)} nodes, {len(edges_df)} edges"
        state['status_classes'] = 'text-sm text-emerald-300'

        nodes_f, edges_f = apply_filters(
            nodes_df,
            edges_df,
            state['filter_type'],
            state['filter_relationship_type'],
            state['filter_search'],
        )

        if selection_state['kind'] == 'node':
            selected_id = str(selection_state['data'].get('id', ''))
            if selected_id and not nodes_f['id'].astype(str).eq(selected_id).any():
                clear_selection()
        elif selection_state['kind'] == 'edge':
            selected_id = str(selection_state['data'].get('id', ''))
            edge_ids = build_cytoscape_elements(nodes_f, edges_f)
            if selected_id and not any(el['data'].get('id') == selected_id for el in edge_ids if 'source' in el['data']):
                clear_selection()

        elements = build_cytoscape_elements(nodes_f, edges_f)
        state['elements'] = elements
        node_elements = sum(1 for element in elements if 'label' in element['data'])
        edge_elements = sum(1 for element in elements if 'source' in element['data'])
        state['built_elements_status'] = f'Rendered: {node_elements} nodes, {edge_elements} edges (filtered)'
        graph = build_networkx_graph(nodes_df, edges_df)
        state['nx_graph'] = graph
        state['networkx_status'] = f'NetworkX (full): {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges'

    try:
        nodes_df, edges_df = load_workbook()
        state['nodes_df'] = nodes_df
        state['edges_df'] = edges_df
        mark_clean()
        refresh_graph_state()
    except (FileNotFoundError, ValueError) as error:
        state['status_text'] = f"Workbook error: {error} Tip: click 'Create Sample Workbook' to generate a starter file."
        state['status_classes'] = 'text-sm text-rose-300'

    with ui.row().classes('w-full h-screen no-wrap bg-slate-100'):
        with ui.column().classes('w-1/5 min-w-60 h-full bg-slate-900 text-white p-4 gap-3'):
            ui.label('Sidebar').classes('text-lg font-semibold')
            status_label = ui.label(state['status_text']).classes(state['status_classes'])
            built_label = ui.label(state['built_elements_status']).classes('text-xs text-emerald-100')
            networkx_label = ui.label(state['networkx_status']).classes('text-xs text-emerald-100')

            with ui.card().classes('w-full bg-slate-800 text-white'):
                ui.label('Validation').classes('text-sm font-semibold')
                error_count_label = ui.label().classes('text-xs text-amber-200')
                copy_errors_button = ui.button('Copy errors').props('outline dense')
                validation_list = ui.column().classes('w-full gap-1 max-h-32 overflow-auto')

            ui.separator().classes('bg-slate-700')
            ui.label('Filters (Graph view)').classes('text-sm text-slate-300')
            dirty_label = ui.label('Saved').classes('text-xs text-emerald-300')

            type_filter = ui.select(
                options=['All', 'Person', 'Place', 'Institution', 'Group'],
                label='Node type',
                value=DEFAULT_NODE_TYPE_FILTER,
            ).classes('w-full')
            rel_filter = ui.select(
                options=[DEFAULT_RELATIONSHIP_FILTER],
                label='relationship_type',
                value=DEFAULT_RELATIONSHIP_FILTER,
            ).classes('w-full')
            label_search = ui.input('Search label contains').props('dense clearable').classes('w-full')
            reset_filters_button = ui.button('Reset Filters').props('outline')

            ui.separator().classes('bg-slate-700')
            ui.label('Navigation').classes('text-sm text-slate-300')
            back_button = ui.button('Back to Graph').props('outline')
            manage_button = ui.button('Manage Nodes').props('outline')
            manage_edges_button = ui.button('Manage Edges').props('outline')
            save_button = ui.button('Save to Excel').props('color=primary')
            demo_button = ui.button('Demo Mode').props('outline')
            sample_button = ui.button('Create Sample Workbook').props('outline')
            export_csv_button = ui.button('Export CSV').props('outline')
            export_gexf_button = ui.button('Export GEXF').props('outline')
            export_summary_button = ui.button('Export Summary').props('outline')

            def refresh_sidebar_status() -> None:
                status_label.set_text(state['status_text'])
                status_label.classes(replace=state['status_classes'])
                built_label.set_text(state['built_elements_status'])
                built_label.set_visibility(bool(state['built_elements_status']))
                networkx_label.set_text(state['networkx_status'])
                networkx_label.set_visibility(bool(state['networkx_status']))
                dirty_label.set_text('Unsaved changes' if is_dirty() else 'Saved')
                dirty_label.classes(replace='text-xs text-amber-300' if is_dirty() else 'text-xs text-emerald-300')

                error_count_label.set_text(f"{len(state['validation_errors'])} error(s)")
                validation_list.clear()
                with validation_list:
                    for error in state['validation_errors']:
                        ui.label(f"• {format_error(error)}").classes('text-xs text-amber-100 break-words')

                disabled = has_validation_errors()
                save_button.disable() if disabled else save_button.enable()
                export_csv_button.disable() if disabled else export_csv_button.enable()
                export_gexf_button.disable() if disabled else export_gexf_button.enable()
                export_summary_button.disable() if disabled else export_summary_button.enable()

        with ui.column().classes('w-3/5 h-full p-6 gap-4'):
            ui.label('Crime Network Viewer').classes('text-2xl font-bold text-slate-800')
            view_container = ui.column().classes('w-full h-full')

        with ui.column().classes('w-1/5 min-w-60 h-full bg-white border-l border-slate-200 p-4 gap-3'):
            ui.label('Inspector').classes('text-lg font-semibold text-slate-800')
            ui.separator()
            inspector_placeholder = ui.label('Select a node/edge to inspect').classes('text-sm text-slate-500')
            inspector_rows = ui.column().classes('w-full gap-2')

    nodes_table = {'element': None}
    edges_table = {'element': None}
    selected_node = {'id': None}
    selected_edge = {'index': None}

    def clear_selection() -> None:
        selection_state.update(kind='none', data={})
        last_selection_signature['value'] = None
        refresh_inspector()

    def confirm_discard_unsaved(on_confirm) -> bool:
        if not is_dirty():
            on_confirm()
            return True

        with ui.dialog() as dialog, ui.card().classes('w-[28rem]'):
            ui.label('Unsaved changes').classes('text-lg font-semibold')
            ui.label('You have unsaved changes. Save first?')

            def save_then_continue() -> None:
                on_save_to_excel()
                if not is_dirty():
                    on_confirm()
                dialog.close()

            def continue_without_saving() -> None:
                on_confirm()
                dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Discard', on_click=continue_without_saving).props('outline color=negative')
                ui.button('Save', on_click=save_then_continue).props('color=primary')
        dialog.open()
        return False

    def copy_errors() -> None:
        if not state['validation_errors']:
            ui.notify('No validation errors to copy', type='info')
            return
        payload = '\n'.join(format_error(error) for error in state['validation_errors'])
        ui.run_javascript(f'navigator.clipboard.writeText({json.dumps(payload)})')
        ui.notify('Errors copied to clipboard', type='positive')

    copy_errors_button.on_click(copy_errors)

    def refresh_inspector() -> None:
        kind = selection_state.get('kind', 'none')
        data = selection_state.get('data', {}) if isinstance(selection_state.get('data'), dict) else {}
        selection_signature = (kind, repr(data))
        if selection_signature == last_selection_signature['value']:
            return
        last_selection_signature['value'] = selection_signature

        inspector_rows.clear()
        if kind == 'none':
            inspector_placeholder.set_visibility(True)
            return

        inspector_placeholder.set_visibility(False)
        with inspector_rows:
            if kind == 'node':
                ui.label(str(data.get('label', ''))).classes('text-lg font-semibold text-slate-900')
                ui.label(f"id: {data.get('id', '')}").classes('text-xs text-slate-500')
                ui.label(f"Type: {data.get('type', '')}").classes('text-sm font-medium text-indigo-700')
                ui.label(str(data.get('description', '') or '')).classes('text-sm text-slate-700')
                core_keys = {'id', 'label', 'type', 'description'}
            else:
                ui.label(str(data.get('relationship_type', ''))).classes('text-lg font-semibold text-slate-900')
                ui.label(f"{data.get('source', '')} → {data.get('target', '')}").classes('text-sm text-slate-600')
                ui.label(str(data.get('description', '') or '')).classes('text-sm text-slate-700')
                core_keys = {'id', 'source', 'target', 'relationship_type', 'description'}

            extras = sorted((k, str(v)) for k, v in data.items() if k not in core_keys)
            with ui.expansion('More fields', value=False).classes('w-full'):
                if not extras:
                    ui.label('(none)').classes('text-xs text-slate-500')
                for key, value in extras:
                    with ui.row().classes('w-full justify-between gap-2 text-sm'):
                        ui.label(key).classes('text-slate-500')
                        ui.label(value).classes('text-slate-800 text-right break-all')

    def render_graph_view() -> None:
        state['active_view'] = 'graph'
        view_container.clear()
        with view_container:
            if state['render_loading']:
                ui.label('Loading…').classes('text-sm text-slate-500')
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

    def set_validation_error_state(errors: list[dict]) -> None:
        state['validation_errors'] = errors
        state['status_text'] = f'Validation errors: {len(errors)}'
        state['status_classes'] = 'text-sm text-amber-300'
        refresh_sidebar_status()

    def apply_edges_update(updated_edges_df) -> bool:
        nodes_df = state['nodes_df']
        if nodes_df is None:
            return False

        errors = validate_data(nodes_df, updated_edges_df)
        if errors:
            set_validation_error_state(errors)
            ui.notify('Cannot apply edge changes due to validation errors', type='warning')
            return False

        state['edges_df'] = updated_edges_df
        mark_dirty()
        refresh_graph_state()
        refresh_sidebar_status()
        refresh_edges_table()
        render_graph_view()
        clear_selection()
        return True

    def on_filter_change() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        state['render_loading'] = bool(nodes_df is not None and edges_df is not None and (len(nodes_df) + len(edges_df) > 300))
        render_graph_view()
        state['filter_type'] = str(type_filter.value or DEFAULT_NODE_TYPE_FILTER)
        state['filter_relationship_type'] = str(rel_filter.value or DEFAULT_RELATIONSHIP_FILTER)
        state['filter_search'] = str(label_search.value or DEFAULT_SEARCH_FILTER)
        refresh_graph_state()
        refresh_sidebar_status()
        state['render_loading'] = False
        render_graph_view()

    def on_filter_change_debounced() -> None:
        filter_debounce['token'] += 1
        current_token = filter_debounce['token']

        def run_if_latest() -> None:
            if current_token != filter_debounce['token']:
                return
            on_filter_change()

        ui.timer(0.25, run_if_latest, once=True)

    def refresh_relationship_filter_options() -> None:
        edges_df = state['edges_df']
        if edges_df is None or 'relationship_type' not in edges_df.columns:
            rel_filter.options = [DEFAULT_RELATIONSHIP_FILTER]
            rel_filter.value = DEFAULT_RELATIONSHIP_FILTER
            return
        values = sorted({str(v) for v in edges_df['relationship_type'].fillna('').tolist() if str(v)})
        options = [DEFAULT_RELATIONSHIP_FILTER, *values]
        rel_filter.options = options
        if rel_filter.value not in options:
            rel_filter.value = DEFAULT_RELATIONSHIP_FILTER
        rel_filter.update()

    def reset_filters() -> None:
        type_filter.value = DEFAULT_NODE_TYPE_FILTER
        rel_filter.value = DEFAULT_RELATIONSHIP_FILTER
        label_search.value = DEFAULT_SEARCH_FILTER
        on_filter_change()

    type_filter.on_value_change(lambda _: on_filter_change_debounced())
    rel_filter.on_value_change(lambda _: on_filter_change_debounced())
    label_search.on_value_change(lambda _: on_filter_change_debounced())

    def current_nodes_rows() -> list[dict]:
        nodes_df = state['nodes_df']
        if nodes_df is None:
            return []
        expected_cols = ['id', 'label', 'type', 'description', 'source_ref', 'date', 'confidence']
        available_cols = [col for col in expected_cols if col in nodes_df.columns]
        return nodes_df[available_cols].fillna('').to_dict('records')

    def refresh_nodes_table() -> None:
        table = nodes_table['element']
        if table is None:
            return
        table.rows = current_nodes_rows()
        table.update()

    def current_edges_rows() -> list[dict]:
        edges_df = state['edges_df']
        if edges_df is None:
            return []
        rows: list[dict] = []
        for index, row in edges_df.iterrows():
            rows.append(
                {
                    'row_id': int(index),
                    'source': str(row.get('source', '') or ''),
                    'target': str(row.get('target', '') or ''),
                    'relationship_type': str(row.get('relationship_type', '') or ''),
                    'description': str(row.get('description', '') or ''),
                    'source_ref': str(row.get('source_ref', '') or ''),
                    'date': str(row.get('date', '') or ''),
                    'confidence': str(row.get('confidence', '') or ''),
                }
            )
        return rows

    def refresh_edges_table() -> None:
        table = edges_table['element']
        if table is None:
            return
        table.rows = current_edges_rows()
        table.update()

    def open_node_dialog(mode: str) -> None:
        editing_id = selected_node['id']
        if mode == 'edit' and not editing_id:
            ui.notify('Select a node row first', type='warning')
            return

        nodes_df = state['nodes_df']
        if nodes_df is None:
            ui.notify('Nodes are not available', type='negative')
            return

        initial = {
            'id': '',
            'label': '',
            'type': NODE_TYPE_OPTIONS[0],
            'description': '',
            'source_ref': '',
            'date': '',
            'confidence': '',
        }
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
                'source_ref': str(row.get('source_ref', '') or ''),
                'date': str(row.get('date', '') or ''),
                'confidence': str(row.get('confidence', '') or ''),
            }

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Node' if mode == 'add' else 'Edit Node').classes('text-lg font-semibold')
            node_id = ui.input('id', value=initial['id'])
            label = ui.input('label', value=initial['label'])
            node_type = ui.select(options=NODE_TYPE_OPTIONS, label='type', value=initial['type'])
            description = ui.textarea('description', value=initial['description'])
            source_ref = ui.input('source_ref (optional)', value=initial['source_ref'])
            date = ui.input('date (YYYY-MM-DD, optional)', value=initial['date'])
            confidence = ui.number('confidence (0-1, optional)', value=initial['confidence'] or None, min=0, max=1)
            error_label = ui.label().classes('text-sm text-rose-600')

            def save_node() -> None:
                id_value = node_id.value.strip() if isinstance(node_id.value, str) else ''
                label_value = label.value.strip() if isinstance(label.value, str) else ''
                type_value = node_type.value if isinstance(node_type.value, str) else ''
                description_value = description.value.strip() if isinstance(description.value, str) else ''
                source_ref_value = source_ref.value.strip() if isinstance(source_ref.value, str) else ''
                date_value = date.value.strip() if isinstance(date.value, str) else ''
                confidence_raw = confidence.value

                if not id_value or not label_value or not type_value:
                    error_label.set_text('id, label, and type are required')
                    return

                if not is_valid_optional_date(date_value):
                    error_label.set_text('date must be empty or use YYYY-MM-DD')
                    return

                confidence_ok, confidence_value = parse_optional_confidence(confidence_raw)
                if not confidence_ok:
                    error_label.set_text('confidence must be empty or a number between 0 and 1')
                    return

                if not is_unique_node_id(nodes_df, id_value, exclude_index=editing_index):
                    error_label.set_text(f"Node id '{id_value}' is already in use")
                    return

                new_row = {
                    'id': id_value,
                    'label': label_value,
                    'type': type_value,
                    'description': description_value,
                    'source_ref': source_ref_value,
                    'date': date_value,
                    'confidence': confidence_value,
                }

                should_store_metadata = any(new_row[column] != '' for column in ('source_ref', 'date', 'confidence'))
                target_nodes_df = nodes_df
                if should_store_metadata or any(col in nodes_df.columns for col in ('source_ref', 'date', 'confidence')):
                    target_nodes_df = ensure_metadata_columns(nodes_df)

                if mode == 'add':
                    state['nodes_df'] = target_nodes_df.loc[:, target_nodes_df.columns].copy()
                    state['nodes_df'].loc[len(state['nodes_df'])] = new_row
                    selected_node['id'] = id_value
                else:
                    state['nodes_df'] = target_nodes_df.copy()
                    for key, value in new_row.items():
                        if key in state['nodes_df'].columns:
                            state['nodes_df'].at[editing_index, key] = value
                    selected_node['id'] = id_value

                mark_dirty()

                refresh_relationship_filter_options()
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
            ui.notify(f"Cannot delete node '{node_id}': referenced by {ref_count} edge(s)", type='warning')
            return

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Delete node?').classes('text-lg font-semibold')
            ui.label(f"Are you sure you want to delete node '{node_id}'?")

            def confirm_delete() -> None:
                state['nodes_df'] = nodes_df[~nodes_df['id'].astype(str).eq(str(node_id))].reset_index(drop=True)
                selected_node['id'] = None
                mark_dirty()
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
        state['active_view'] = 'manage_nodes'
        view_container.clear()
        with view_container:
            with ui.card().classes('w-full h-full bg-white'):
                ui.label('Manage Nodes').classes('text-xl font-semibold text-slate-800')
                ui.label('Add, edit, or delete nodes in memory. Use "Save to Excel" to persist changes.').classes(
                    'text-sm text-slate-500'
                )
                columns = [
                    {'name': 'id', 'label': 'id', 'field': 'id', 'required': True, 'align': 'left'},
                    {'name': 'label', 'label': 'label', 'field': 'label', 'align': 'left'},
                    {'name': 'type', 'label': 'type', 'field': 'type', 'align': 'left'},
                    {'name': 'description', 'label': 'description', 'field': 'description', 'align': 'left'},
                    {'name': 'source_ref', 'label': 'source_ref', 'field': 'source_ref', 'align': 'left'},
                    {'name': 'date', 'label': 'date', 'field': 'date', 'align': 'left'},
                    {'name': 'confidence', 'label': 'confidence', 'field': 'confidence', 'align': 'left'},
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

    def open_edge_dialog(mode: str) -> None:
        edges_df = state['edges_df']
        nodes_df = state['nodes_df']
        editing_index = selected_edge['index']

        if edges_df is None or nodes_df is None:
            ui.notify('Data is not available', type='negative')
            return

        if mode == 'edit' and editing_index is None:
            ui.notify('Select an edge row first', type='warning')
            return

        initial = {
            'source': '',
            'target': '',
            'relationship_type': '',
            'description': '',
            'source_ref': '',
            'date': '',
            'confidence': '',
        }
        if mode == 'edit':
            if editing_index not in edges_df.index:
                ui.notify('Selected edge no longer exists', type='warning')
                return
            row = edges_df.loc[editing_index]
            initial = {
                'source': str(row.get('source', '') or ''),
                'target': str(row.get('target', '') or ''),
                'relationship_type': str(row.get('relationship_type', '') or ''),
                'description': str(row.get('description', '') or ''),
                'source_ref': str(row.get('source_ref', '') or ''),
                'date': str(row.get('date', '') or ''),
                'confidence': str(row.get('confidence', '') or ''),
            }

        node_options = {str(row['id']): f"{row['id']} — {row.get('label', '')}" for _, row in nodes_df.iterrows()}

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Edge' if mode == 'add' else 'Edit Edge').classes('text-lg font-semibold')
            source = ui.select(options=node_options, label='source', value=initial['source'])
            target = ui.select(options=node_options, label='target', value=initial['target'])
            relationship_type = ui.input('relationship_type', value=initial['relationship_type'])
            description = ui.textarea('description', value=initial['description'])
            source_ref = ui.input('source_ref (optional)', value=initial['source_ref'])
            date = ui.input('date (YYYY-MM-DD, optional)', value=initial['date'])
            confidence = ui.number('confidence (0-1, optional)', value=initial['confidence'] or None, min=0, max=1)
            error_label = ui.label().classes('text-sm text-rose-600')

            def save_edge() -> None:
                source_value = str(source.value or '').strip()
                target_value = str(target.value or '').strip()
                rel_value = str(relationship_type.value or '').strip()
                description_value = str(description.value or '').strip()
                source_ref_value = str(source_ref.value or '').strip()
                date_value = str(date.value or '').strip()
                confidence_raw = confidence.value

                ok, message = can_add_or_edit_edge(nodes_df, source_value, target_value, rel_value)
                if not ok:
                    error_label.set_text(message)
                    return

                if not is_valid_optional_date(date_value):
                    error_label.set_text('date must be empty or use YYYY-MM-DD')
                    return

                confidence_ok, confidence_value = parse_optional_confidence(confidence_raw)
                if not confidence_ok:
                    error_label.set_text('confidence must be empty or a number between 0 and 1')
                    return

                should_store_metadata = any(
                    value != '' for value in (source_ref_value, date_value, confidence_value)
                ) or any(col in edges_df.columns for col in ('source_ref', 'date', 'confidence'))
                updated_edges_df = ensure_metadata_columns(edges_df) if should_store_metadata else edges_df.copy()
                if mode == 'add':
                    row_data = {col: '' for col in updated_edges_df.columns}
                    row_data.update(
                        {
                            'source': source_value,
                            'target': target_value,
                            'relationship_type': rel_value,
                            'description': description_value,
                            'source_ref': source_ref_value,
                            'date': date_value,
                            'confidence': confidence_value,
                        }
                    )
                    updated_edges_df.loc[len(updated_edges_df)] = row_data
                    selected_edge['index'] = updated_edges_df.index[-1]
                else:
                    updated_edges_df.at[editing_index, 'source'] = source_value
                    updated_edges_df.at[editing_index, 'target'] = target_value
                    updated_edges_df.at[editing_index, 'relationship_type'] = rel_value
                    updated_edges_df.at[editing_index, 'description'] = description_value
                    if 'source_ref' in updated_edges_df.columns:
                        updated_edges_df.at[editing_index, 'source_ref'] = source_ref_value
                    if 'date' in updated_edges_df.columns:
                        updated_edges_df.at[editing_index, 'date'] = date_value
                    if 'confidence' in updated_edges_df.columns:
                        updated_edges_df.at[editing_index, 'confidence'] = confidence_value
                    selected_edge['index'] = editing_index

                if apply_edges_update(updated_edges_df):
                    refresh_relationship_filter_options()
                    dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Save', on_click=save_edge)

        dialog.open()

    def delete_selected_edge() -> None:
        edges_df = state['edges_df']
        editing_index = selected_edge['index']
        if edges_df is None:
            ui.notify('Data is not available', type='negative')
            return
        if editing_index is None or editing_index not in edges_df.index:
            ui.notify('Select an edge row first', type='warning')
            return

        row = edges_df.loc[editing_index]
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Delete edge?').classes('text-lg font-semibold')
            ui.label(
                f"Delete edge '{row.get('source', '')} → {row.get('target', '')}' ({row.get('relationship_type', '')})?"
            )

            def confirm_delete() -> None:
                updated_edges_df = edges_df.drop(index=editing_index)
                selected_edge['index'] = None
                if apply_edges_update(updated_edges_df):
                    refresh_relationship_filter_options()
                    dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Delete', on_click=confirm_delete).props('outline color=negative')

        dialog.open()

    def render_manage_edges_view() -> None:
        state['active_view'] = 'manage_edges'
        view_container.clear()
        with view_container:
            with ui.card().classes('w-full h-full bg-white'):
                ui.label('Manage Edges').classes('text-xl font-semibold text-slate-800')
                ui.label('Add, edit, or delete edges in memory. Use "Save to Excel" to persist changes.').classes(
                    'text-sm text-slate-500'
                )
                columns = [
                    {'name': 'source', 'label': 'source', 'field': 'source', 'required': True, 'align': 'left'},
                    {'name': 'target', 'label': 'target', 'field': 'target', 'required': True, 'align': 'left'},
                    {
                        'name': 'relationship_type',
                        'label': 'relationship_type',
                        'field': 'relationship_type',
                        'required': True,
                        'align': 'left',
                    },
                    {'name': 'description', 'label': 'description', 'field': 'description', 'align': 'left'},
                    {'name': 'source_ref', 'label': 'source_ref', 'field': 'source_ref', 'align': 'left'},
                    {'name': 'date', 'label': 'date', 'field': 'date', 'align': 'left'},
                    {'name': 'confidence', 'label': 'confidence', 'field': 'confidence', 'align': 'left'},
                ]
                edges_table['element'] = ui.table(
                    columns=columns,
                    rows=current_edges_rows(),
                    row_key='row_id',
                    selection='single',
                    pagination={'rowsPerPage': 10},
                ).classes('w-full')

                def on_row_select(event) -> None:
                    row = event.args.get('added', [])
                    if row:
                        selected_edge['index'] = int(row[0].get('row_id'))

                edges_table['element'].on('selection', on_row_select)

                with ui.row().classes('gap-2 mt-2'):
                    ui.button('Add', on_click=lambda: open_edge_dialog('add'))
                    ui.button('Edit', on_click=lambda: open_edge_dialog('edit')).props('outline')
                    ui.button('Delete', on_click=delete_selected_edge).props('outline color=negative')

    render_graph_view()
    refresh_relationship_filter_options()
    refresh_sidebar_status()

    def on_save_to_excel() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            ui.notify('Nothing to save: workbook data is not loaded', type='warning')
            return
        if has_validation_errors():
            ui.notify('Cannot save: fix validation errors first', type='warning')
            return

        try:
            save_workbook(nodes_df, edges_df)
        except RuntimeError as error:
            ui.notify(str(error), type='negative')
            return

        mark_clean()
        refresh_sidebar_status()
        ui.notify(f'Saved to {workbook_label}', type='positive')

    def on_export_csv() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            ui.notify('Cannot export: workbook data is not loaded', type='warning')
            return
        if has_validation_errors():
            ui.notify('Cannot export CSV: fix validation errors first', type='warning')
            return

        nodes_path, edges_path = export_csv(nodes_df, edges_df)
        ui.notify(f'Exported CSV: {nodes_path}, {edges_path}', type='positive')

    def on_export_gexf() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            ui.notify('Cannot export: workbook data is not loaded', type='warning')
            return
        if has_validation_errors():
            ui.notify('Cannot export GEXF: fix validation errors first', type='warning')
            return

        nx_graph = state['nx_graph']
        if nx_graph is None:
            nx_graph = build_networkx_graph(nodes_df, edges_df)
            state['nx_graph'] = nx_graph

        gexf_path = export_gexf(nx_graph)
        ui.notify(f'Exported GEXF: {gexf_path}', type='positive')

    def on_export_summary() -> None:
        nodes_df = state['nodes_df']
        edges_df = state['edges_df']
        if nodes_df is None or edges_df is None:
            ui.notify('Cannot export summary: workbook data is not loaded', type='warning')
            return
        if has_validation_errors():
            ui.notify('Cannot export summary: fix validation errors first', type='warning')
            return

        summary_path = export_summary(nodes_df, edges_df)
        ui.notify(f'Exported summary: {summary_path}', type='positive')

    def apply_loaded_workbook(nodes_df, edges_df) -> bool:
        validation_errors = validate_data(nodes_df, edges_df)
        if validation_errors:
            set_validation_error_state(validation_errors)
            ui.notify('Sample workbook validation failed unexpectedly', type='negative')
            return False

        state['nodes_df'] = nodes_df
        state['edges_df'] = edges_df
        mark_clean()
        refresh_relationship_filter_options()
        refresh_graph_state()
        refresh_sidebar_status()
        refresh_nodes_table()
        refresh_edges_table()
        render_graph_view()
        clear_selection()
        return True

    def create_sample_and_reload() -> None:
        created_path = create_sample_workbook(str(workbook_path))
        nodes_df, edges_df = load_workbook(str(workbook_path))
        if apply_loaded_workbook(nodes_df, edges_df):
            reset_filters()
            render_graph_view()
            ui.notify(f'Created sample workbook at {created_path}', type='positive')

    def on_demo_mode() -> None:
        def load_existing() -> None:
            try:
                nodes_df, edges_df = load_workbook(str(workbook_path))
            except (FileNotFoundError, ValueError) as error:
                ui.notify(f'Cannot load workbook: {error}', type='negative')
                return
            if apply_loaded_workbook(nodes_df, edges_df):
                reset_filters()
                render_graph_view()
                ui.notify('Demo Mode loaded existing workbook', type='positive')

        def overwrite_with_sample() -> None:
            create_sample_and_reload()

        if not workbook_path.exists():
            overwrite_with_sample()
            return

        with ui.dialog() as dialog, ui.card().classes('w-[30rem]'):
            ui.label('Demo Mode').classes('text-lg font-semibold')
            ui.label(f'{workbook_label} already exists. Load it as-is, or overwrite with sample data?')

            def run_overwrite() -> None:
                def proceed() -> None:
                    overwrite_with_sample()

                confirm_discard_unsaved(proceed)
                dialog.close()

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('outline')
                ui.button('Load existing', on_click=lambda: (load_existing(), dialog.close())).props('outline')
                ui.button('Overwrite with sample', on_click=run_overwrite).props('color=primary')
        dialog.open()

    def on_create_sample_workbook() -> None:
        if workbook_path.exists():
            with ui.dialog() as dialog, ui.card().classes('w-96'):
                ui.label('Overwrite existing workbook?').classes('text-lg font-semibold')
                ui.label(f'{workbook_label} already exists. This will replace it.')

                def confirm_overwrite() -> None:
                    create_sample_and_reload()
                    dialog.close()

                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=dialog.close).props('outline')
                    ui.button('Overwrite', on_click=confirm_overwrite)
            dialog.open()
            return

        create_sample_and_reload()

    manage_button.on_click(render_manage_nodes_view)
    manage_edges_button.on_click(render_manage_edges_view)

    def on_back_to_graph() -> None:
        if state['active_view'] in {'manage_nodes', 'manage_edges'}:
            confirm_discard_unsaved(render_graph_view)
            return
        render_graph_view()

    back_button.on_click(on_back_to_graph)
    save_button.on_click(on_save_to_excel)
    reset_filters_button.on_click(reset_filters)
    demo_button.on_click(on_demo_mode)
    sample_button.on_click(on_create_sample_workbook)
    export_csv_button.on_click(on_export_csv)
    export_gexf_button.on_click(on_export_gexf)
    export_summary_button.on_click(on_export_summary)

    ui.timer(0.1, refresh_inspector)


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(title='Crime Network App (Phase 0)')
