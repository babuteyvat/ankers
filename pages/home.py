from nicegui import ui

# ==========================================
# CUSTOM STYLE SHEET INITIALIZATION
# ==========================================
ui.add_head_html('''
<style>
    /* Hide the native toggle chevron icon completely */
    .q-expansion-item__toggle-icon {
        display: none !important;
    }
    /* Enforce layout padding styles across list trees */
    .q-expansion-item__container .q-item {
        padding-left: 0px !important;
        padding-right: 0px !important;
        min-height: 36px !important;
    }
    /* Hide settings icon by default */
    .deck-container .deck-settings-btn {
        opacity: 0;
        transition: opacity 0.15s ease-in-out;
        pointer-events: none;
    }
    /* Display settings icon cleanly on hover over the layout container */
    .deck-container:hover .deck-settings-btn {
        opacity: 1;
        pointer-events: auto;
    }
    /* FIXED: Pure CSS rule to create beautifully spaced out sketchy lines */
    .sketch-dotted-btn {
        border: 1.5px dashed rgba(100, 116, 139, 0.4) !important; /* Semi-transparent border */
        background-color: transparent !important;
        transition: all 0.2s ease-in-out;
    }
    .sketch-dotted-btn:hover {
        border-color: rgba(100, 116, 139, 0.8) !important;
        background-color: rgba(226, 232, 240, 0.4) !important;
    }
</style>
''')

ui.query('body').classes('bg-slate-50 text-slate-800 antialiased')

# Global styling configuration shortcuts
ACTIVE_STYLE = 'bg-blue-50 text-blue-600 border-blue-200 font-bold'
INACTIVE_STYLE = 'text-slate-600 hover:bg-slate-200 border-transparent font-medium'

# Backend state data tracking container
app_state = {'current_deck': 'Physics Stuff'}
deck_elements_pool = []


# ==========================================
# SELECTION CONTROLLER FUNCTION
# ==========================================
def select_deck(target_name, row_element):
    app_state['current_deck'] = target_name
    sub_decks = ['Listening', 'Reading', 'Formulas']

    # Loop over tracked rows to reset them to standard unselected states
    for element in deck_elements_pool:
        is_sub = element.context_tag in sub_decks
        # Tightened padding (py-0.5) to keep folder groups visually dense
        pad_cls = 'pl-6 py-0.5' if is_sub else 'pl-2 py-1.5'
        element.classes(
            replace=f'deck-container w-full flex items-center justify-between rounded-lg cursor-pointer border {INACTIVE_STYLE} {pad_cls}')

    # Apply active high-contrast blue tracking styles to the selected element
    is_target_sub = target_name in sub_decks
    target_pad = 'pl-6 py-0.5' if is_target_sub else 'pl-2 py-1.5'
    row_element.classes(
        replace=f'deck-container w-full flex items-center justify-between rounded-lg cursor-pointer border {ACTIVE_STYLE} {target_pad}')

    # Update active display text live
    main_display_title.text = f'Active Workspace: {target_name}'

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
            with ui.expansion('JP Course').classes('w-full text-slate-700 font-medium').props(
                    'dense default-opened') as exp_jp:
                with exp_jp.add_slot('header'):
                    with ui.row().classes('items-center gap-2 w-full py-1'):
                        jp_open = ui.icon('arrow_drop_down')
                        jp_closed = ui.icon('arrow_right').classes('hidden')
                        ui.label('JP Course').classes('text-sm font-semibold text-slate-700')

                exp_jp.on('show', lambda: [jp_open.classes(remove='hidden'), jp_closed.classes(add='hidden')])
                exp_jp.on('hide', lambda: [jp_open.classes(add='hidden'), jp_closed.classes(remove='hidden')])

                # Sub-Deck 1: Listening (With bullet dot and tighter vertical spacing)
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                        'click', lambda: select_deck('Listening', row_list)) as row_list:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')  # Smaller, lighter sub-dot
                        ui.label('Listening').classes('text-sm')
                    ui.button(icon='settings', color='slate-500').props('flat round dense size=sm').classes(
                        'deck-settings-btn')
                row_list.context_tag = 'Listening'
                deck_elements_pool.append(row_list)

                # Sub-Deck 2: Reading (With bullet dot and tighter vertical spacing)
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                        'click', lambda: select_deck('Reading', row_read)) as row_read:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')
                        ui.label('Reading').classes('text-sm')
                    ui.button(icon='settings', color='slate-500').props('flat round dense size=sm').classes(
                        'deck-settings-btn')
                row_read.context_tag = 'Reading'
                deck_elements_pool.append(row_read)

            # --- FOLDER 2: Trig Identities ---
            with ui.expansion('Trig Identities').classes('w-full text-slate-700 font-medium').props(
                    'dense') as exp_trig:
                with exp_trig.add_slot('header'):
                    with ui.row().classes('items-center gap-2 w-full py-1'):
                        trig_open = ui.icon('arrow_drop_down').classes('hidden')
                        trig_closed = ui.icon('arrow_right')
                        ui.label('Trig Identities').classes('text-sm font-semibold text-slate-700')

                exp_trig.on('show', lambda: [trig_open.classes(remove='hidden'), trig_closed.classes(add='hidden')])
                exp_trig.on('hide', lambda: [trig_open.classes(add='hidden'), trig_closed.classes(remove='hidden')])

                # Sub-Deck 3: Formulas (With bullet dot and tighter vertical spacing)
                with ui.row().classes(
                        f'deck-container w-full flex items-center justify-between py-0.5 rounded-lg cursor-pointer border {INACTIVE_STYLE} pl-6').on(
                        'click', lambda: select_deck('Formulas', row_form)) as row_form:
                    with ui.row().classes('items-center gap-2 no-wrap'):
                        ui.icon('fiber_manual_record', size='6px').classes('text-slate-400')
                        ui.label('Formulas').classes('text-sm')
                    ui.button(icon='settings', color='slate-500').props('flat round dense size=sm').classes(
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
                ui.button(icon='settings', color='blue-500').props('flat round dense size=sm').classes(
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
                ui.button(icon='settings', color='slate-500').props('flat round dense size=sm').classes(
                    'deck-settings-btn')
            row_kor.context_tag = 'Korean words'
            deck_elements_pool.append(row_kor)

            # --- QUICK ADD DECK BUTTON ---
            # Increased width (w-44), balanced the text visibility, and applied the fixed custom outline class
            ui.button('+ add more', color='transparent') \
                .props('flat dense') \
                .classes(
                'text-xs mt-6 mx-auto w-44 py-1.5 font-bold tracking-widest text-slate-500/80 lowercase rounded-full sketch-dotted-btn block')

        ui.space()

    # ------------------------------------------
    # BOTTOM FIXED UTILITY TOOLBAR
    # ------------------------------------------
    with ui.row().classes('w-full gap-1 pt-4 border-t border-slate-200 items-center bg-slate-100 pl-2 pr-2'):
        # Circular settings button on the bottom left
        ui.button(icon='settings', color='transparent').classes(
            'text-slate-600 hover:bg-slate-200 p-1 min-h-0 min-w-0 shadow-none cursor-pointer').props(
            'flat round dense')

# Persistent label on right canvas to explicitly verify selection toggles
main_display_title = ui.label('Active Workspace: Physics Stuff').classes(
    'p-8 md:pl-12 text-slate-800 font-bold text-xl')

ui.run()
