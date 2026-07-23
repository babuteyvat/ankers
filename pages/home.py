from nicegui import app, ui

# Mount your static assets directory
app.add_static_files('/static', 'static')

# Link the external CSS stylesheet
ui.add_head_html('<link rel="stylesheet" href="/static/style.css">')

ui.query('body').classes('bg-slate-50 text-slate-800 antialiased')

# Global styling configuration shortcuts
ACTIVE_STYLE = 'bg-blue-50 text-blue-600 border-blue-200 font-bold'
INACTIVE_STYLE = 'text-slate-600 hover:bg-slate-200 border-transparent font-medium'

# Backend state data tracking container
app_state = {'current_deck': 'Physics Stuff'}
deck_elements_pool = []

# ==========================================
# SETTINGS POPUP MODAL SYSTEM
# ==========================================
settings_dialog = ui.dialog()

with settings_dialog, ui.card().classes('rounded-xl p-5 bg-white shadow-xl w-80'):
    # Top row containing the 'X' close button on the top right
    with ui.row().classes('w-full items-center justify-end mb-3'):
        ui.button(icon='close', color='transparent', on_click=settings_dialog.close).classes(
            'text-slate-400 hover:text-slate-700 p-0 min-h-0 min-w-0 shadow-none cursor-pointer'
        ).props('flat round dense size=sm')

    dialog_content_label = ui.label('Settings configuration').classes('text-sm text-slate-700 font-medium')

def open_settings(target_name):
    dialog_content_label.text = f'Settings for: {target_name}'
    settings_dialog.open()

# ==========================================
# SELECTION CONTROLLER FUNCTION
# ==========================================
def select_deck(target_name, row_element):
    app_state['current_deck'] = target_name
    sub_decks = ['Listening', 'Reading', 'Formulas']

    # Loop over tracked rows to reset them to standard unselected states
    for element in deck_elements_pool:
        is_sub = element.context_tag in sub_decks
        pad_cls = 'pl-6 py-0.5' if is_sub else 'pl-2 py-1.5'
        element.classes(
            replace=f'deck-container w-full flex items-center justify-between rounded-lg cursor-pointer border {INACTIVE_STYLE} {pad_cls}')

    # Apply active high-contrast blue tracking styles to the selected element
    is_target_sub = target_name in sub_decks
    target_pad = 'pl-6 py-0.5' if is_target_sub else 'pl-2 py-1.5'
    row_element.classes(
        replace=f'deck-container w-full flex items-center justify-between rounded-lg cursor-pointer border {ACTIVE_STYLE} {target_pad}')

    # [MODIFIED] Update the main dashboard title cleanly
    dashboard_title.text = target_name

# ==========================================
# RESPONSIVE HEADER (Visible on small screens)
# ==========================================
with ui.header().classes(
        'bg-slate-100 text-slate-800 border-b border-slate-200 p-3 md:hidden flex items-center justify-between'):
    ui.button(icon='menu', color='slate-700', on_click=lambda: sidebar.toggle()).props('flat round dense')
    ui.label('ANKERS').classes('font-black tracking-wider text-slate-700 text-lg')
    ui.element('div').classes('w-8')

# ==========================================
# LEFT SIDEBAR NAVIGATION
# ==========================================
with ui.left_drawer(value=True, fixed=True).props('breakpoint=768') as sidebar:
    sidebar.classes('bg-slate-100 p-6 flex flex-col justify-between border-r border-slate-200 h-full overflow-hidden')

    # Top Branding Header
    with ui.column().classes('w-full items-start mb-4'):
        ui.label('ANKERS').classes('text-2xl font-bold tracking-wider text-slate-800 pl-2')

    # ------------------------------------------
    # SCROLLABLE DECKS CONTAINER TREE
    # ------------------------------------------
    with ui.column().classes('w-full flex-1 overflow-y-auto pr-1 items-center'):
        ui.space()

        with ui.column().classes('max-w-[200px] w-full gap-2 items-start justify-start'):
            # Section title block decoration line
            with ui.row().classes('w-full items-center gap-2 mb-2 no-wrap'):
                ui.label('Decks').classes('text-sm font-bold text-slate-700 tracking-wide')
                ui.element('div').classes('flex-1 h-[1px] bg-slate-400')

            # --- FOLDER 1: JP Course ---
            jp_state = {'open': False}
            with ui.row().classes(
                    'deck-container items-center justify-between w-full py-1 px-2 rounded-lg cursor-pointer border border-transparent hover:bg-slate-200 text-slate-700 font-medium'):
                with ui.row().classes('items-center gap-2 no-wrap flex-1').on('click', lambda: [
                    jp_state.update(open=not jp_state['open']),
                    jp_arrow_open.classes(toggle='hidden'),
                    jp_arrow_closed.classes(toggle='hidden'),
                    jp_content.classes(toggle='hidden')
                ]):
                    jp_arrow_open = ui.icon('arrow_drop_down').classes('hidden')
                    jp_arrow_closed = ui.icon('arrow_right')
                    ui.label('JP Course').classes('text-sm font-semibold text-slate-700')

                ui.button(icon='edit', color='slate-500', on_click=lambda: open_settings('JP Course')).props(
                    'flat round dense size=sm').classes('deck-settings-btn')

            with ui.column().classes('w-full gap-2 pl-2 hidden') as jp_content:
                # Sub-Deck 1: Listening
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                    'click', lambda: select_deck('Listening', row_list)) as row_list:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')
                        ui.label('Listening').classes('text-sm')
                    ui.button(icon='settings', color='slate-500',
                              on_click=lambda: open_settings('Listening')).props(
                        'flat round dense size=sm').classes(
                        'deck-settings-btn')
                row_list.context_tag = 'Listening'
                deck_elements_pool.append(row_list)

                # Sub-Deck 2: Reading
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                    'click', lambda: select_deck('Reading', row_read)) as row_read:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')
                        ui.label('Reading').classes('text-sm')
                    ui.button(icon='settings', color='slate-500', on_click=lambda: open_settings('Reading')).props(
                        'flat round dense size=sm').classes(
                        'deck-settings-btn')
                row_read.context_tag = 'Reading'
                deck_elements_pool.append(row_read)

            # --- FOLDER 2: Trig Identities ---
            trig_state = {'open': False}
            with ui.row().classes(
                    'deck-container items-center justify-between w-full py-1 px-2 rounded-lg cursor-pointer border border-transparent hover:bg-slate-200 text-slate-700 font-medium'):
                with ui.row().classes('items-center gap-2 no-wrap flex-1').on('click', lambda: [
                    trig_state.update(open=not trig_state['open']),
                    trig_arrow_open.classes(toggle='hidden'),
                    trig_arrow_closed.classes(toggle='hidden'),
                    trig_content.classes(toggle='hidden')
                ]):
                    trig_arrow_open = ui.icon('arrow_drop_down').classes('hidden')
                    trig_arrow_closed = ui.icon('arrow_right')
                    ui.label('Trig Identities').classes('text-sm font-semibold text-slate-700')

                ui.button(icon='edit', color='slate-500', on_click=lambda: open_settings('Trig Identities')).props(
                    'flat round dense size=sm').classes('deck-settings-btn')

            with ui.column().classes('w-full gap-2 pl-2 hidden') as trig_content:
                # Sub-Deck 3: Formulas
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                    'click', lambda: select_deck('Formulas', row_form)) as row_form:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')
                        ui.label('Formulas').classes('text-sm')
                    ui.button(icon='settings', color='slate-500', on_click=lambda: open_settings('Formulas')).props(
                        'flat round dense size=sm').classes(
                        'deck-settings-btn')
                row_form.context_tag = 'Formulas'
                deck_elements_pool.append(row_form)

                # --- DECK 3: Physics Stuff (Selected by Default) ---
            with ui.row().classes(
                    f'deck-container w-full flex items-center justify-between py-1.5 rounded-lg cursor-pointer border {ACTIVE_STYLE} pl-2').on(
                'click', lambda: select_deck('Physics Stuff', row_phys)) as row_phys:
                with ui.row().classes('items-center gap-2 no-wrap'):
                    ui.icon('fiber_manual_record', size='8px').classes('text-slate-700')
                    ui.label('Physics Stuff').classes('text-sm truncate')
                ui.button(icon='settings', color='blue-500', on_click=lambda: open_settings('Physics Stuff')).props(
                    'flat round dense size=sm').classes(
                    'deck-settings-btn')
            row_phys.context_tag = 'Physics Stuff'
            deck_elements_pool.append(row_phys)

            # --- DECK 4: Korean Words ---
            with ui.row().classes(
                    f'deck-container w-full flex items-center justify-between py-1.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-2').on(
                'click', lambda: select_deck('Korean words', row_kor)) as row_kor:
                with ui.row().classes('items-center gap-2 no-wrap'):
                    ui.icon('fiber_manual_record', size='8px').classes('text-slate-700')
                    ui.label('Korean words').classes('text-sm truncate')
                ui.button(icon='settings', color='slate-500', on_click=lambda: open_settings('Korean words')).props(
                    'flat round dense size=sm').classes(
                    'deck-settings-btn')
            row_kor.context_tag = 'Korean words'
            deck_elements_pool.append(row_kor)

            # --- QUICK ADD DECK BUTTON ---
            ui.button('add more', color='transparent') \
                .props('flat dense') \
                .classes(
                'text-xs mt-6 mx-auto w-44 py-1.5 font-bold tracking-widest text-slate-500/80 lowercase rounded-full sketch-dotted-btn block')

        ui.space()

        # ------------------------------------------
        # BOTTOM FIXED UTILITY TOOLBAR
        # ------------------------------------------
        with ui.row().classes(
                'w-full gap-1 pt-4 border-t border-slate-200 items-center bg-slate-100 pl-2 pr-2'):
            ui.button(icon='settings', color='transparent', on_click=lambda: open_settings('General Settings')).classes(
                'text-slate-600 hover:text-slate-900 p-1 min-h-0 min-w-0 shadow-none cursor-pointer').props(
                'flat round dense')

# ==========================================
# MAIN CONTENT AREA (Dashboard)
# ==========================================
with ui.column().classes('flex-1 px-8 md:px-12 pt-30 pb-12 gap-8 items-center justify-start w-full min-h-screen'):
    # Centered container, nudged just slightly above vertical center
    with ui.column().classes('w-full max-w-5xl gap-8 items-center'):

        # Main Deck Title (left-aligned above the content cards)
        dashboard_title = ui.label(app_state['current_deck']).classes(
            'text-3xl font-extrabold text-slate-900 tracking-tight self-start')

        # --- TOP ROW: ACTION CARDS ---
        with ui.row().classes('w-full gap-6 items-stretch'):

            def action_card(title, count, icon_name, btn_text='Start >'):
                with ui.column().classes(
                        'p-8 bg-white border border-slate-200 rounded-2xl gap-6 flex-1 shadow-sm hover:shadow-md transition-shadow'):
                    with ui.row().classes('items-center gap-4'):
                        ui.icon(icon_name, size='3rem').classes('text-slate-500')
                        with ui.column().classes('gap-0'):
                            ui.label(title).classes('text-lg font-bold text-slate-800')
                            ui.label(f'({count})').classes('text-sm text-slate-500 font-medium')

                    with ui.row().classes('w-full gap-3 mt-auto pt-4'):
                        ui.button(btn_text).classes(
                            'flex-1 text-sm bg-slate-900 text-white rounded-xl px-6 py-3 font-semibold')
                        ui.button('options').props('flat').classes('text-sm text-slate-600 rounded-xl px-4 font-medium')


            action_card('Lessons', 15, 'school')
            action_card('Review', 20, 'history', btn_text='Review >')

        # State tracker for the activity heatmap year
        activity_state = {'year': 2026}

        # --- SECOND ROW: ACTIVITY HEATMAP (Multi-year support) ---
        with ui.column().classes('w-full p-8 bg-white border border-slate-200 rounded-2xl gap-4 shadow-sm'):

            @ui.refreshable
            def render_heatmap():
                current_year = activity_state['year']
                is_current_year = (current_year >= 2026)

                # Card Header with Year Navigation
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label('Activity').classes('text-lg font-bold text-slate-800')
                    with ui.row().classes('items-center gap-1.5'):
                        ui.icon('chevron_left', size='sm').classes(
                            'cursor-pointer hover:text-slate-800 text-slate-500').on('click', lambda: change_year(-1))
                        ui.label(str(current_year)).classes('text-sm font-medium text-slate-700')
                        if is_current_year:
                            ui.icon('chevron_right', size='sm').classes('text-slate-300 cursor-not-allowed')
                        else:
                            ui.icon('chevron_right', size='sm').classes(
                                'cursor-pointer hover:text-slate-800 text-slate-500').on('click',
                                                                                         lambda: change_year(1))

                activity_summary_label = ui.label(f'Jul 24, {current_year} / Lessons 0, Review 2').classes(
                    'text-s text-slate-500 font-medium order-last mt-2')

                with ui.column().classes('w-full gap-1.5 pt-2 pb-1'):
                    from datetime import date, timedelta
                    import random

                    d_start = date(current_year, 1, 1)
                    d_end = date(current_year, 12, 31)

                    def get_sunday_first_index(d):
                        return (d.weekday() + 1) % 7

                    start_padding = get_sunday_first_index(d_start)

                    weeks = []
                    current_week = [None] * 7
                    for i in range(start_padding):
                        current_week[i] = None

                    curr = d_start
                    while curr <= d_end:
                        idx = get_sunday_first_index(curr)
                        current_week[idx] = curr
                        if idx == 6:
                            weeks.append(current_week)
                            current_week = [None] * 7
                        curr += timedelta(days=1)

                    if any(current_week[i] is not None for i in range(7)):
                        weeks.append(current_week)

                    num_weeks = len(weeks)

                    # Month Labels Row aligned to exact grid columns
                    with ui.element('div').classes(
                            f'grid grid-cols-[24px_repeat({num_weeks},minmax(0,1fr))] gap-1 w-full items-center h-5'):
                        ui.element('div')

                        month_start_weeks = {}
                        for w_idx, wk in enumerate(weeks):
                            for day in wk:
                                if day and day.day == 1:
                                    m_name = day.strftime('%b')
                                    if m_name not in month_start_weeks.values():
                                        month_start_weeks[w_idx] = m_name

                        for w_idx in range(num_weeks):
                            with ui.element('div').classes('relative'):
                                if w_idx in month_start_weeks:
                                    ui.label(month_start_weeks[w_idx]).classes(
                                        'absolute left-0 text-[11px] font-medium text-slate-500 whitespace-nowrap')

                    dow = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

                    def make_click_handler(d_obj, l_cnt, r_cnt):
                        date_str = d_obj.strftime('%b %d, %Y')
                        return lambda: activity_summary_label.set_text(f'{date_str} / Lessons {l_cnt}, Review {r_cnt}')

                    for r_idx, day_name in enumerate(dow):
                        with ui.element('div').classes(
                                f'grid grid-cols-[24px_repeat({num_weeks},minmax(0,1fr))] gap-1 w-full items-center'):
                            ui.label(day_name).classes('text-xs text-slate-400 font-medium text-center')

                            for week in weeks:
                                day_obj = week[r_idx]
                                if day_obj is None:
                                    ui.element('div').classes('w-full aspect-square bg-transparent')
                                else:
                                    seed_val = day_obj.toordinal()
                                    local_rand = random.Random(seed_val)

                                    color = 'bg-slate-100 hover:bg-slate-400'
                                    l_count = local_rand.randint(0, 5)
                                    r_count = local_rand.randint(0, 10)

                                    val = local_rand.random()
                                    if val > 0.7:
                                        color = 'bg-slate-300 hover:bg-slate-500'
                                        l_count = local_rand.randint(5, 15)
                                        r_count = local_rand.randint(10, 25)
                                    if val > 0.9:
                                        color = 'bg-slate-800 hover:bg-slate-900'
                                        l_count = local_rand.randint(15, 35)
                                        r_count = local_rand.randint(25, 60)

                                    ui.element('div').classes(
                                        f'w-full aspect-square rounded-sm cursor-pointer transition-colors {color}'
                                    ).on('click', make_click_handler(day_obj, l_count, r_count))


            def change_year(delta):
                activity_state['year'] += delta
                render_heatmap.refresh()


            render_heatmap()

ui.run()