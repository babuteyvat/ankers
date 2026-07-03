from nicegui import ui

flashcards = [
    {"q": "What is the capital of Japan?", "a": "Tokyo", "state": "learning", "step": 0, "history": []},
    {"q": "What is the Japanese word for 'Thank you'?", "a": "Arigatou", "state": "learning", "step": 0, "history": []},
    {"q": "What is $5 \\times 5$?", "a": "25", "state": "learning", "step": 0, "history": []}
]

class Card_Manager():
    def __init__(self):
        self.current_index = 0
        self.is_flipped = False

    def next_card(self, card_text):
        self.current_index += 1
        if self.current_index != len(flashcards):
            card_text.set_text(flashcards[self.current_index]["q"])
        else:
            ui.notify('done')

    def flip_card(self, card_text):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            card_text.set_text(flashcards[self.current_index]["a"])
        else:
            card_text.set_text(flashcards[self.current_index]["q"])

ui.add_head_html('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
}
.card-panel {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05);
}
</style>
''')

Card = Card_Manager()

with ui.column().classes('items-center w-full q-pa-md'):
    ui.label("Anki").classes('text-h4 q-mb-md')

    with ui.card().classes('w-96 h-64 flex flex-center cursor-pointer q-mb-md') as card:
        card_text = ui.label(flashcards[Card.current_index]["q"]).classes('text-h5 text-center')
        card.on('click', lambda: Card.flip_card(card_text))

    with ui.row().classes('q-gutter-md'):
        ui.button("Easy", on_click=lambda: Card.next_card(card_text))
        ui.button("Good", on_click=lambda: ui.notify('e'))
        ui.button("Hard", on_click=lambda: ui.notify('we'))
        ui.button("Again", on_click=lambda: ui.notify('wee'))

ui.run()


