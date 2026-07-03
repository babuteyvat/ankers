from nicegui import ui
import theme


def create():
    theme.frame("Study Page")

    with ui.column().classes('w-full items-center pt-32 px-6'):
        # Placeholder Container
        with ui.card().classes('w-full max-w-3xl items-center p-12 text-center bg-white shadow-lg'):
            ui.icon('school', size='4em', color=theme.THEME['primary'])
            ui.label('Study Session').classes('text-3xl font-bold mt-4')
            ui.label('Flashcard logic will go here.').classes('text-gray-500 mb-8')

            # Temporary Back Button
            ui.button('Back to Home', on_click=lambda: ui.navigate.to('/')) \
                .props('flat') \
                .style(f"color: {theme.THEME['secondary']}")