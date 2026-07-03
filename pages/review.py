from nicegui import ui
import theme


def create():
    theme.frame("Review Page")

    with ui.column().classes('w-full items-center pt-32 px-6'):
        # Placeholder Container
        with ui.card().classes('w-full max-w-3xl items-center p-12 text-center bg-white shadow-lg'):
            ui.icon('history', size='4em', color='#FF7675')
            ui.label('Review Summary').classes('text-3xl font-bold mt-4')
            ui.label('Statistics and past sessions will go here.').classes('text-gray-500 mb-8')