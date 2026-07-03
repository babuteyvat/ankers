# pages/home.py
from nicegui import ui
import theme  # Import your shared styles


def create():
    # 1. Apply shared styles and header
    theme.frame("")

    # 2. Main Page Container
    # 'pt-32' ensures content starts below the floating header
    with ui.column().classes('w-full min-h-screen items-center pt-32 px-6 gap-10'):
        # --- Hero Section ---
        with ui.column().classes('items-center text-center gap-2'):
            ui.label('Master Your Knowledge').style(f"color: {theme.THEME['text_main']}").classes('text-5xl font-black')
            ui.label('Simple, efficient, and beautiful flashcards.').style(
                f"color: {theme.THEME['text_light']}").classes('text-xl font-medium')

        # --- Stats Dashboard ---
        with ui.row().classes('flex-wrap justify-center gap-6 w-full max-w-5xl'):
            # Helper to create stat cards (defined locally as it's specific to Home)
            def stat_card(title, value, subtext, color_hex):
                with ui.card().style(f"border-left: 6px solid {color_hex}").classes('w-72 shadow-lg'):
                    ui.label(title).classes('text-sm font-bold text-gray-400 uppercase tracking-wider')
                    ui.label(value).style(f"color: {color_hex}").classes('text-4xl font-black my-1')
                    ui.label(subtext).classes('text-gray-500 text-sm')

            stat_card('Reviews Due', '142', 'You are falling behind!', '#FF7675')  # Reddish color
            stat_card('Cards Learned', '850', 'Top 10% of users', theme.THEME['secondary'])
            stat_card('Current Streak', '12 Days', 'Keep it up!', theme.THEME['primary'])

        # --- Action Buttons ---
        with ui.column().classes('items-center gap-4 mt-8'):
            # Primary "Start" Button
            ui.button('Start Review Session', icon='play_arrow', on_click=lambda: ui.navigate.to('/study')) \
                .style(f"background-color: {theme.THEME['primary']}; color: white") \
                .classes('w-64 h-14 text-xl font-bold rounded-full shadow-lg hover:scale-105 transition-transform')

            # Secondary "Create" Button
            ui.button('Create New Deck', icon='add', on_click=lambda: ui.navigate.to('/deck-maker')) \
                .props('flat') \
                .style(f"color: {theme.THEME['text_light']}")