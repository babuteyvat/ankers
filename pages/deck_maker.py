from nicegui import ui
import theme


def create():
    theme.frame("Deck Maker")

    with ui.column().classes('w-full items-center pt-32 px-6'):
        # Placeholder Container
        with ui.card().classes('w-full max-w-4xl items-center p-12 text-center bg-white shadow-lg'):
            ui.icon('construction', size='4em', color=theme.THEME['secondary'])
            ui.label('Deck Builder').classes('text-3xl font-bold mt-4')
            ui.label('Form inputs for creating new cards will go here.').classes('text-gray-500 mb-8')