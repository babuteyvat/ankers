from nicegui import ui
import sqlite3
from random import *

conn = sqlite3.connect(':memory:')

c = conn.cursor()

flashcards_def = [
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
    c.execute("INSERT OR IGNORE INTO vars (id, current_day) VALUES (1, 0)")
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards(
            id INTEGER PRIMARY KEY,
            q TEXT NOT NULL,
            a TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'learning',
            step INTEGER NOT NULL DEFAULT 0
    )
    """)

#c.executemany("INSERT OR IGNORE INTO flashcard VALUES (?, ?, ?, ?, ?)", flashcards_def)

class Card_Manager():
    def __init__(self):
        self.current_index = 0
        self.is_flipped = False
        self.load_db()
        self.new_old()
    #make two tables, one for vars and one for flashcards, pull flashcards using UID
    def load_db(self):
        c.execute("SELECT * FROM flashcards WHERE state = :state", {"state": "learning"})
        self.learning_cards = c.fetchall()
        c.execute("SELECT * FROM flashcards WHERE state = :state", {"state": "reviewing"})
        self.reviewing_cards = c.fetchall()
        c.execute("SELECT current_day FROM vars")
        result = c.fetchone()
        self.current_day = result[0]
    
    def save_db(self, card_id, new_state, new_step):
        with conn:
            c.execute("""
                UPDATE flashcards
                SET state = ?, step = ?
                WHERE id = ?
            """, [new_state, new_step, card_id])
            c.execute("UPDATE vars SET current_day = ? WHERE id = 1", [self.current_day])

    def flip_card(self, card_text):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            card_text.set_text(flashcards_def[self.current_index][2])
        else:
            card_text.set_text(flashcards_def[self.current_index][1])
    def new_old(self):
        self.new_cards = []
        self.old_cards = []
        self.review_cards = []
        for card in self.learning_cards:
            if card[5] == 0:
                self.new_cards.append(card)
            elif card[5] != 0 and card[4] == "reviewing":
                self.review_cards.append(card)
            else:
                self.old_cards.append(card)

Card = Card_Manager()

class Session():
    def __init__(self):
        self.build_up()
        self.study_amount = 20
        Card.current_day += 1
        
    def build_up(self):
        self.queue = []
        for c in Card.new_cards:
            while len(self.queue) < self.study_amount/4:
                self.queue.append(c)
        for c in Card.old_cards:
            while len(self.queue) < self.study_amount:
                self.queue.append(c)
        if Card.review_cards:
            for c in Card.review_cards:
                while len(self.queue) < self.study_amount*4: 
                    #add something to prevent infinite looping due to not having enough review cards
                    self.queue.append(c)
        shuffle(self.queue)

    def next_card(self, card_text):
            card_text.set_text(self.queue[Card.current_index][1])
    
    def grade_easy(self, card_text):
        self.queue[Card.current_index][4] == "reviewing"
        self.queue[Card.current_index][5]
        Card.save_db(card_id=self.queue[Card.current_index][0], new_state=self.queue[Card.current_index][4], new_step=self.queue[Card.current_index][5])
        self.next_card(card_text)

    def grade_good(self, card_text):
        self.queue[Card.current_index][5] += 1
        if self.queue[Card.current_index][5] == 3:
            self.queue[Card.current_index][4] == "reviewing"
        else:
            self.queue[Card.current_index][4] == "learning"
        self.queue.pop(Card.current_index)
        Card.save_db(card_id=self.queue[Card.current_index][0], new_state=self.queue[Card.current_index][4], new_step=self.queue[Card.current_index][5])
        self.next_card(card_text)

    def grade_hard(self, card_text):
        self.queue.pop(Card.current_index)
        self.queue.append(Card.current_index)
        Card.save_db(card_id=self.queue[Card.current_index][0], new_state=self.queue[Card.current_index][4], new_step=self.queue[Card.current_index][5])
        self.next_card(card_text)

    def grade_again(self, card_text):
        self.queue[Card.current_index][4] == "learning"
        self.queue[Card.current_index][5] == 0
        self.queue.pop(Card.current_index)
        self.queue.append(Card.current_index)
        Card.save_db(card_id=self.queue[Card.current_index][0], new_state=self.queue[Card.current_index][4], new_step=self.queue[Card.current_index][5])
        self.next_card(card_text)

        # normally grade_difficulty would have an additional factor "ease" factor to make it more retainable but for
        # presentation purposes, it will only use this part just to show that the deck is working


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
        card_text = ui.label(flashcards_def[Card.current_index][1]).classes('text-h5 text-center')
        card.on('click', lambda: Card.flip_card(card_text))

    with ui.row().classes('q-gutter-md'):
        ui.button("Again", on_click=lambda: Card.grade_again(card_text))
        ui.button("Hard", on_click=lambda: Card.grade_hard(card_text))
        ui.button("Good", on_click=lambda: Card.grade_good(card_text))
        ui.button("Easy", on_click=lambda: Card.grade_easy(card_text))
        

ui.run()