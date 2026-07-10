from nicegui import ui
import sqlite3
from random import *

conn = sqlite3.connect(':memory:')

c = conn.cursor()

flashcards = [
    {"id": 1, "q": "What is the capital of Japan?", "a": "Tokyo", "state": "learning", "step": 0},
    {"id": 2, "q": "What is the Japanese word for 'Thank you'?", "a": "Arigatou", "state": "learning", "step": 0},
    {"id": 3, "q": "What is $5 \\times 5$?", "a": "25", "state": "learning", "step": 0}
]

with conn:
    c.execute("""
        CREATE TABLE IF NOT EXISTS vars(
              id INTEGER PRIMARY KEY,
            current_day INTEGER DEFAULT 0
    )
    """)
    c. execute("INSERT OR IGNORE INTO vars (id, current_day) VALUES (1, 0)")
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards(
            id INTEGER PRIMARY KEY,
            q TEXT NOT NULL
            a TEXT NOT NULL
            state TEXT NOT NULL DEFAULT 'learning'
            step INTEGER NOT NULL DEFAULT 0
    )
    """)

class Card_Manager():
    def __init__(self):
        self.current_index = 0
        self.is_flipped = False
        self.load_db()
        self.new_old()
    #make two tables, one for vars and one for flashcards, pull flashcards using UID
    def load_db(self):
        c.execute("SELECT * FROM flashcards WHERE state:=state", {"state": "learning"})
        self.learning_cards = c.fetchall()
        c.execute("SELECT * FROM flashcards WHERE state:=state", {"state": "reviewing"})
        self.reviewing_cards = c.fetchall()
        c.execute("SELECT current_day FROM vars")
        result = c.fetchone()
        self.current_day = result[0]
    
    def save_db(self):
        with conn:
            c.execute("UPDATE * FROM flashcards")

    def flip_card(self, card_text):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            card_text.set_text(flashcards[self.current_index]["a"])
        else:
            card_text.set_text(flashcards[self.current_index]["q"])
    def new_old(self):
        for card in self.carding:
            return card

Card = Card_Manager()

class Session():
    def __init__(self):
        self.build_up()
        self.study_amount = 20
        
    def build_up(self):
        self.queue = []
        for c in Card.new_cards:
            while len(self.queue) < self.study_amount/4:
                self.queue.append(c)
        for c in Card.old_cards:
            while len(self.queue) < self.study_amount:
                self.queue.append(c)

    def next_card(self, card_text):
        self.current_index += 1
        if self.current_index != len(flashcards):
            card_text.set_text(self.queue[self.current_index]["q"])
        else:
            ui.notify('done')

    def grade_easy(self):
        self.queue[self.current_index][5]
    def grade_good(self):
        self.queue[self.current_index][5]
    def grade_hard(self):
        self.queue[self.current_index][5]
    def grade_again(self):
        self.queue[self.current_index][5]

    def evaluate(self):
        flashcard_id = self.queue[self.current_index][0]


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

with ui.column().classes('items-center w-full q-pa-md'):
    ui.label("Anki").classes('text-h4 q-mb-md')

    with ui.card().classes('w-96 h-64 flex flex-center cursor-pointer q-mb-md') as card:
        card_text = ui.label(flashcards[Card.current_index]["q"]).classes('text-h5 text-center')
        card.on('click', lambda: Card.flip_card(card_text))

    with ui.row().classes('q-gutter-md'):
        ui.button("Again", on_click=lambda: ui.notify('wee'))
        ui.button("Hard", on_click=lambda: ui.notify('we'))
        ui.button("Good", on_click=lambda: ui.notify('e'))
        ui.button("Easy", on_click=lambda: Card.next_card(card_text))
        

ui.run()

#rwrj