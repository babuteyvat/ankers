from nicegui import ui
import sqlite3
from random import shuffle
from datetime import date
import atexit

conn = sqlite3.connect(':memory:')

c = conn.cursor()

flashcards_def = [
    {"id": 1, "q": "What is the capital of Japan?", "a": "Tokyo", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0},
    {"id": 2, "q": "What is the Japanese word for 'Thank you'?", "a": "Arigatou", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0},
    {"id": 3, "q": "What is $5 \\times 5$?", "a": "25", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0}
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
            step INTEGER NOT NULL DEFAULT 0,
            days_till_review INTEGER NOT NULL DEFAULT 0,
            review_count INTEGER NOT NULL DEFAULT 0
            
    )
    """)

#deckmaker starts here
c.execute("CREATE TABLE IF NOT EXISTS deckstats(name TEXT)")
#run on startup

deckname = "deck1"
#variable to name deck

class Deckmaker():
    def __init__(self, deckname):
        self.deckname = deckname
    def createdeck(self):
        c.execute(f"""CREATE TABLE IF NOT EXISTS
        {self.deckname}(id INTEGER,
        question TEXT,
        answer TEXT,
        state TEXT,
        step INTEGER,
        days_till_review INTEGER,
        review_count INTEGER)""")
#function that creates deck based on deckname variable. Prolly wanna make input prompt that changes deckname when making card maker layout

    def createcard(self, q, a):
        deckIDs = c.execute(f"SELECT id from {deckname}")
        idvalue = len(deckIDs.fetchall()) + 1
        c.execute(f"INSERT INTO {deckname} VALUES(?, ?, ?, 'learning', 0, 0, 0)", (idvalue, q, a))
        c.commit()
#function to create card and add to selected deck. Ideally the input prompts have some sort of check to confirm uploadable data types.
#The first input variable is the name of the deck. Each subsequent variable is for a key in the dictionary. Note that they're being
#made into a database.

    def upload(self):
        for row in c.execute(f"SELECT question, answer, state, step, days_till_review, review_count FROM {self.deckname}"):
            newID = len(flashcards_def) + 1
            flashcards_def.append({"id": newID, "q": row[0], "a": [1], "state": row[2], "step": row[3], "days_till_review": row[4], "review_count": row[5]})
#FOR UPLOADING TO CARD POOL. Run this function with table name in database.

lessons_tally = 0
reviews_tally = 0
#FIND WAY TO IMPLEMENT IN MAIN FUNCTION.

def calldate():
    c.execute("""CREATE TABLE IF NOT EXISTS
    heatmaptable(index INTEGER,
    date INTEGER,
    month INTEGER,
    year INTEGER
    lessons_done INTEGER,
    reveiws_done INTEGER,
    streak INTEGER)""")
    today = date.today()
    date = today.day
    month = today.month
    year = today.year
    dmy = c.execute("SELECT * FROM heatmaptable ORDER BY index DESCEND LIMIT 1")
    if dmy[0] == (date - 1 and dmy[1] == month and dmy[2] == year) or (dmy[0] == 1 and dmy[1] == month - 1 and dmy[2] == year) or (dmy[0] == 1 and dmy[1] == 1 and dmy[2] == year - 1):
        streak = 0
    else:
        streak = 1    
    c.execute("DELETE FROM heatmaptable WHERE date = ? AND month = ? AND year = ?", (date, month, year))
    c.execute("INSERT INTO heatmaptable VALUES(?, ?, ?, ?, ?, ?)", (date, month, year, lessons_tally, reviews_tally, streak))
    conn.commit()

atexit.register(calldate)


#retrieves date and lessons/reviews tally to track on heatmap. Runs on exiting the program.

c.executemany("INSERT OR IGNORE INTO flashcard VALUES (?, ?, ?, ?, ?, ?, ?)", flashcards_def)

class Card_Manager():
    def __init__(self):
        self.load_db()
        self.new_old()

    def load_db(self):
        c.execute("SELECT * FROM flashcards WHERE state = 'learning'")
        self.learning_cards = c.fetchall()
        c.execute("SELECT * FROM flashcards WHERE state = 'reviewing'")
        self.reviewing_cards = c.fetchall()
        c.execute("SELECT current_day FROM vars WHERE id = 1")
        result = c.fetchone()
        if result:
            self.current_day = result[0]
        else: self.current_day = 0
    
    def save_db(self, card_id, new_state, new_step, new_days_till_review, new_review_count):
        with conn:
            c.execute("""
                UPDATE flashcards
                SET state = ?, step = ?, days_till_review = ?, review_count = ?
                WHERE id = ?
            """, (new_state, new_step, new_days_till_review, new_review_count, card_id))
            c.execute("UPDATE vars SET current_day = ? WHERE id = 1", (self.current_day,))
        #might need to put this down in session class because of how flashcards are (they are not queue)

    def new_old(self):
        self.new_cards = []
        self.old_cards = []
        self.review_cards = []
        for card in self.learning_cards:
            if card[4] == 0:
                self.new_cards.append(card)
            else:
                self.old_cards.append(card)
                
        self.review_cards = list(self.reviewing_cards)

Card = Card_Manager()

class Session():
    def __init__(self):
        self.build_up()
        self.study_amount = 20
        Card.current_day += 1 #might need to look at cus what it do
        self.is_flipped = False
        self.current_index = 0
        
    def build_up(self):
        self.queue = []

        for c in Card.new_cards[:int(self.study_amount/4)]:
                self.queue.append(c)
        for c in Card.old_cards[:int(self.study_amount)]:
                self.queue.append(c)
        if Card.review_cards:
            target = int(self.study_amount*4)
            added = 0
            for c in Card.review_cards:

                card_list = list(c)

                card_list[5] = card_list[5] - 1
                if card_list[5] == 0:
                    card_list[6] += 1
                    # check review count, if its max review then pop
                    if card_list[6] > 6:
                        # review complete, relable as completed so it wont be pulled by load db()
                        card_list[3] = "completed"
                        Card.save_db(card_id=card_list[0], 
                        new_state=card_list[3], 
                        new_step=card_list[4],
                        new_days_till_review= card_list[5],
                        new_review_count=card_list[6])

                    else:
                        if added < target:
                            self.queue.append(tuple(card_list))
                            added += 1
                        else:
                            # for cards that are already due but the list is full then to counteract card_list[5] = card_list[5] - 1 and card_list[6] += 1, this is added
                            card_list[5] = 1
                            card_list[6] = card_list[6] - 1

                        Card.save_db(card_id=card_list[0], 
                        new_state=card_list[3], 
                        new_step=card_list[4],
                        new_days_till_review= card_list[5],
                        new_review_count=card_list[6])
                else:
                    Card.save_db(card_id=card_list[0], 
                    new_state=card_list[3], 
                    new_step=card_list[4],
                    new_days_till_review= card_list[5],
                    new_review_count=card_list[6])

        shuffle(self.queue)

    def next_card(self, card_text):
            card_text.set_text(self.queue[self.current_index])

    def flip_card(self, card_text):
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            card_text.set_text(self.queue[self.current_index][2])
        else:
            card_text.set_text(self.queue[self.current_index][1])
    
    def grade_easy(self, card_text):
        self.review_check()

        card_list = list(self.queue[self.current_index])

        card_list[3] = "reviewing"
        Card.save_db(card_id=card_list[0], 
                     new_state=card_list[3], 
                     new_step=card_list[4],
                     new_days_till_review= card_list[5],
                     new_review_count=card_list[6])
        
        self.queue.pop(self.current_index)
        self.next_card(card_text)

    def grade_good(self, card_text):
        self.review_check()

        card_list = list(self.queue[self.current_index])

        card_list[4] += 1
        if card_list[4] >= 3:
            card_list[3] = "reviewing"
        else:
            card_list[3] = "learning"
        Card.save_db(card_id=card_list[0], 
                new_state=card_list[3], 
                new_step=card_list[4],
                new_days_till_review= card_list[5],
                new_review_count=card_list[6])
        
        self.queue.pop(self.current_index)
        self.next_card(card_text)

    def grade_hard(self, card_text):
        self.review_check()

        card_list = list(self.queue[self.current_index])

        Card.save_db(card_id=card_list[0], 
                new_state=card_list[3], 
                new_step=card_list[4],
                new_days_till_review= card_list[5],
                new_review_count=card_list[6])
        
        card = self.queue.pop(self.current_index)
        self.queue.append(tuple(card))
        self.next_card(card_text)

    def grade_again(self, card_text):
        self.review_check()

        card_list = list(self.queue[self.current_index])

        card_list[3] = "learning"
        card_list[4] = 0
        card_list[5] = 0
        card_list[6] = 0

        Card.save_db(card_id=card_list[0], 
                new_state=card_list[3], 
                new_step=card_list[4],
                new_days_till_review= card_list[5],
                new_review_count=card_list[6])
        
        card = self.queue.pop(self.current_index)
        self.queue.append(tuple(card))
        self.next_card(card_text)

    def review_check(self):
        card_list = list(self.queue[self.current_index])
        if card_list[3] == "reviewing" and card_list[5] == 0:
            global review_tally
            review_tally += 1
            if card_list[6] == 0:
                card_list[5] = 1
            elif card_list[6] == 1:
                card_list[5] = 2
            elif card_list[6] == 2:
                card_list[5] = 4
            elif card_list[6] == 3:
                card_list[5] = 7
            elif card_list[6] == 4:
                card_list[5] = 14
            elif card_list[6] == 5:
                card_list[5] = 28
            elif card_list[6] == 6:
                card_list[5] = 56
        else:
            global lessons_tally
            lessons_tally += 1
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

session = Session()

with ui.column().classes('items-center w-full q-pa-md'):
    ui.label("Anki").classes('text-h4 q-mb-md')

    with ui.card().classes('w-96 h-64 flex flex-center cursor-pointer q-mb-md') as card:
        card_text = ui.label(flashcards_def[session.current_index][1]).classes('text-h5 text-center')
        card.on('click', lambda: session.flip_card(card_text))

    with ui.row().classes('q-gutter-md'):
        ui.button("Again", on_click=lambda: session.grade_again(card_text))
        ui.button("Hard", on_click=lambda: session.grade_hard(card_text))
        ui.button("Good", on_click=lambda: session.grade_good(card_text))
        ui.button("Easy", on_click=lambda: session.grade_easy(card_text))
        

ui.run()