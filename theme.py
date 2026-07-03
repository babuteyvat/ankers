# theme.py
from nicegui import ui

# change color hex stuff
THEME = {
    'primary': '#6C5CE7',    # Main buttons/accents
    'secondary': '#00B894',  # Success/Secondary actions
    'background': '#DFE6E9', # background for the page
    'header_bg': '#FFFFFF',  # header
    'text_main': '#2D3436',  # text
    'text_light': '#636E72', # subtitles
}


# wraps page content with custom Header, Font, and Styles.
def frame(page_title):

    # custom fonts from google
    ui.add_head_html('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Commissioner:wght@100..900&display=swap" rel="stylesheet">
                <style>
            body {
                font-family: 'Commissioner', sans-serif;
                background-color: ''' + THEME['background'] + ''';
            }
            .floating-header {
                background-color: ''' + THEME['header_bg'] + ''';
                color: ''' + THEME['text_main'] + ''';
            }
        </style>
    ''')

    # 2. Create the Standard "Hanging" Header
    # Removed: 'm-4', 'rounded-xl', 'bg-transparent'
    # Added: Direct background color application
    with ui.header().classes('shadow-lg p-4 justify-between items-center') \
            .style(f"background-color: {THEME['header_bg']}; color: {THEME['text_main']}"):
        # Left: Logo
        with ui.row().classes('items-center gap-2'):
            ui.icon('style', size='md', color=THEME['primary'])
            ui.label(page_title).classes('text-xl font-extrabold tracking-wide')

        # Center: Navigation
        with ui.row().classes('gap-6'):
            def nav_link(text, target):
                ui.link(text, target) \
                    .style(f"color: {THEME['text_main']}") \
                    .classes('no-underline font-bold hover:opacity-70 transition-opacity')

            nav_link('Home', '/')
            nav_link('Study', '/study')
            nav_link('Review', '/review')
            nav_link('Deck Maker', '/deck-maker')

        # Right: Settings
        with ui.row().classes('items-center'):
            with ui.button(icon='settings').props('flat round color=grey-8'):
                with ui.menu().classes('w-64 p-4'):
                    ui.label('Settings').classes('text-lg font-bold mb-4')
                    ui.switch('Dark Mode').bind_value(ui.dark_mode())
                    ui.separator().classes('my-2')
                    ui.button('Log Out', icon='logout').props('flat full-width align=left color=red')