from nicegui import ui

flashcards = [
    {"q": "What is the capital of Japan?", "a": "Tokyo"},
    {"q": "What is the Japanese word for 'Thank you'?", "a": "Arigatou"},
    {"q": "What is $5 \\times 5$?", "a": "25"}
]

current_index = 0
is_flipped = False

def next_card():
    global current_index
    current_index += 1
    if current_index != len(flashcards):
         card_text.set_text(flashcards[current_index]["q"])
    else:
        ui.notify('done')

def flip_card():
    global is_flipped
    is_flipped = not is_flipped
    if is_flipped:
        card_text.set_text(flashcards[current_index]["a"])
    else:
        card_text.set_text(flashcards[current_index]["q"])

with ui.column().classes('items-center w-full q-pa-md'):
    ui.label("Anki").classes('text-h4 q-mb-md')
    
    with ui.card().classes('w-96 h-64 flex flex-center cursor-pointer q-mb-md').on('click', flip_card):
        card_text = ui.label(flashcards[current_index]["q"]).classes('text-h5 text-center')
    with ui.row().classes('q-gutter-md'):
        ui.button("Easy", on_click= next_card)
        ui.button("Good", on_click=lambda: ui.notify('e'))
        ui.button("Hard", on_click=lambda: ui.notify('we'))
        ui.button("Again", on_click=lambda: ui.notify('wee'))

ui.run()


