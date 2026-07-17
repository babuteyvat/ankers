from nicegui import ui
import sqlite3
from random import shuffle

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
    for card in flashcards_def:
        c.execute("INSERT OR IGNORE INTO flashcards (id, q, a, state, step, days_till_review, review_count) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                  (card["id"], card["q"], card["a"], card["state"], card["step"], card["days_till_review"], card["review_count"]))
#c.executemany("INSERT OR IGNORE INTO flashcard VALUES (?, ?, ?, ?, ?, ?, ?)", flashcards_def)

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
    
    def add_card(self, q, a):
        with conn:
            c.execute("""
                INSERT INTO flashcards (q, a, state, step, days_till_review, review_count) 
                VALUES (?, ?, 'learning', 0, 0, 0)
            """, (q, a))
        
        self.load_db()
        self.new_old()

Card = Card_Manager()

class Session():
    def __init__(self):
        # UI State Variables
        self.typed_answer = ""
        self.is_answered = False
        self.is_correct = False
        self.is_flipped = False
        
        self.study_amount = 20
        Card.current_day += 1 
        self.build_up()
        
    def build_up(self):
        # Split into two distinct queues
        self.wani_queue = []
        self.anki_queue = []

        # Wani Queue: Gets new and old learning cards
        for c in Card.new_cards[:int(self.study_amount/4)]:
            self.wani_queue.append(c)
        for c in Card.old_cards[:int(self.study_amount)]:
            self.wani_queue.append(c)
            
        # Anki Queue: Gets review cards
        if Card.review_cards:
            target = int(self.study_amount*4)
            added = 0
            for c in Card.review_cards:
                card_list = list(c)
                card_list[5] = card_list[5] - 1
                
                if card_list[5] <= 0:
                    card_list[6] += 1
                    if card_list[6] > 6:
                        card_list[3] = "completed"
                        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
                    else:
                        if added < target:
                            self.anki_queue.append(tuple(card_list))
                            added += 1
                        else:
                            card_list[5] = 1
                            card_list[6] = card_list[6] - 1
                        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
                else:
                    Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])

        shuffle(self.wani_queue)
        shuffle(self.anki_queue)

    # --- UI INTERACTION LOGIC ---
    def check_answer_wani(self):
        if not self.wani_queue: return
        correct_ans = self.wani_queue[0][2].lower()
        self.is_correct = (self.typed_answer.strip().lower() == correct_ans)
        self.is_answered = True
        flashcard_ui.refresh()

    def flip_anki(self):
        if not self.anki_queue: return
        self.is_flipped = True
        anki_ui.refresh()

    def prep_next(self, mode):
        self.typed_answer = ""
        self.is_answered = False
        self.is_flipped = False
        if mode == "wani":
            flashcard_ui.refresh()
        elif mode == "anki":
            anki_ui.refresh()

    # --- GRADING LOGIC ---
    def get_queue(self, mode):
        # Helper to grab the right queue based on the game mode
        return self.wani_queue if mode == "wani" else self.anki_queue

    def review_check(self, card_list):
        if card_list[3] == "reviewing" and card_list[5] == 0:
            if card_list[6] == 0: card_list[5] = 1
            elif card_list[6] == 1: card_list[5] = 2
            elif card_list[6] == 2: card_list[5] = 4
            elif card_list[6] == 3: card_list[5] = 7
            elif card_list[6] == 4: card_list[5] = 14
            elif card_list[6] == 5: card_list[5] = 28
            elif card_list[6] == 6: card_list[5] = 56
        return card_list

    def grade_easy(self, mode):
        q = self.get_queue(mode)
        if not q: return
        card_list = list(q[0])
        card_list[3] = "reviewing"
        card_list = self.review_check(card_list)

        
        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
        
        q.pop(0) # Remove from active deck
        self.prep_next(mode)

    def grade_good(self, mode):
        q = self.get_queue(mode)
        if not q: return
        card_list = list(q[0])

        card_list[4] += 1
        if card_list[4] >= 3:
            card_list[3] = "reviewing"
        else:
            card_list[3] = "learning"

        card_list = self.review_check(card_list)
            
        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
        
        q.pop(0)
        self.prep_next(mode)

    def grade_hard(self, mode):
        q = self.get_queue(mode)
        if not q: return
        card_list = list(q[0])
        card_list = self.review_check(card_list)

        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
        
        # Move to back of the line
        card = q.pop(0)
        q.append(tuple(card))
        self.prep_next(mode)

    def grade_again(self, mode):
        q = self.get_queue(mode)
        if not q: return
        card_list = list(q[0])
        card_list = self.review_check(card_list)

        card_list[3] = "learning"
        card_list[4] = 0
        card_list[5] = 0
        card_list[6] = 0

        Card.save_db(card_list[0], card_list[3], card_list[4], card_list[5], card_list[6])
        
        # Move to back of the line
        card = q.pop(0)
        q.append(tuple(card))
        self.prep_next(mode)

    def advance_day(self):

        Card.current_day += 1

        with conn:
            c.execute("UPDATE vars SET current_day = ? WHERE id = 1", (Card.current_day,))
            
        Card.load_db()
        Card.new_old()
        self.build_up()
        home_ui.refresh()
session = Session()
   
        
        # normally grade_difficulty would have an additional factor "ease" factor to make it more retainable but for
        # presentation purposes, it will only use this part just to show that the deck is working


ui.add_head_html('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
body { 
    font-family: 'Inter', sans-serif; 
    background-color: #f4f4f5; /* Light gray background */
}
/* Custom class for the sketchy/boxy card look */
.sketch-card {
    background-color: #ffffff;
    border: 2px solid #1e293b; /* Thick dark slate border */
    border-radius: 0.25rem;
    box-shadow: 4px 4px 0px rgba(30,41,59,1); /* Hard shadow */
}
</style>
''')

#The Hub UI
def show_home():
    home_container.set_visibility(True)
    lesson_container.set_visibility(False)
    review_container.set_visibility(False)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(False)
    #home_ui.refresh() # This updates the Day and Card counts!

def show_lesson():
    home_container.set_visibility(False)
    lesson_container.set_visibility(True)
    review_container.set_visibility(False)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(False)
    session.typed_answer = ""
    session.is_answered = False
    flashcard_ui.refresh()

def show_review():
    home_container.set_visibility(False)
    lesson_container.set_visibility(False)
    review_container.set_visibility(True)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(False)
    session.is_flipped = False
    anki_ui.refresh()

def show_addcards():
    home_container.set_visibility(False)
    lesson_container.set_visibility(False)
    review_container.set_visibility(False)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(True)

def show_decks():
    home_container.set_visibility(False)
    lesson_container.set_visibility(False)
    review_container.set_visibility(False)
    decks_container.set_visibility(True)
    addcards_container.set_visibility(False)
    decks_ui.refresh()

with ui.column().classes("w-full max-w-[480px] mx-auto p-4 mt-4"):
    

    # --- VIEW 1: HUB ---
    home_container = ui.column().classes("w-full")
    with home_container:
        
        @ui.refreshable
        def home_ui():
            # Top Bar with the Next Day Trigger
            with ui.row().classes("w-full items-center justify-between border-b-2 border-slate-800 pb-2 mb-4"):
                ui.label("ANKERS").classes("text-xl font-bold tracking-widest text-slate-800")
                with ui.row().classes("gap-2 items-center"):
                    ui.label(f"Day {Card.current_day}").classes("text-xs font-bold px-2 py-1 bg-slate-200 text-slate-800 rounded")
                    ui.button("Next Day", on_click=session.advance_day).classes("bg-slate-800 text-white text-xs font-bold py-1 px-2 rounded shadow-none")

            with ui.row().classes("w-full gap-4 justify-between"):
                # LESSONS CARD
                with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                    ui.label(f"Lessons ({len(session.wani_queue)})").classes("font-bold text-slate-800 text-lg")
                    ui.icon('local_library', size='3.5rem').classes('text-slate-300 my-2') 
                    ui.button("Start >", on_click=show_lesson).classes("w-full bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")

                # REVIEW CARD
                with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                    ui.label(f"Review List ({len(session.anki_queue)})").classes("font-bold text-slate-800 text-lg")
                    ui.icon('assignment', size='3.5rem').classes('text-slate-300 my-2')
                    ui.button("Start >", on_click=show_review).classes("w-full bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")

            with ui.row().classes("w-full gap-4 justify-between mt-4"):
                # CARD LIST
                with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                    ui.label(f"Card Directory").classes("font-bold text-slate-800 text-lg")
                    ui.icon('list_alt', size='3.5rem').classes('text-slate-300 my-2')
                    ui.button("View Decks >", on_click=show_decks).classes("w-full bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")

        # This runs it for the first time when the app starts!
        home_ui()

    #wani MODE
    lesson_container = ui.column().classes("w-full items-center")
    with lesson_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        ui.label("Wani Mode (Typing)").classes('text-2xl font-bold mb-4 text-slate-800')

        # We make this refreshable so it switches from Input -> Grading seamlessly
        @ui.refreshable
        def flashcard_ui():
            if not session.wani_queue:
                with ui.column().classes("w-full items-center text-center mt-8"):
                    ui.label("🎉").classes("text-6xl mb-4")
                    ui.label("All done!").classes("text-2xl font-bold text-slate-800")
                return
            
            current_card = session.wani_queue[0]

            # The Flashcard Window
            with ui.card().classes('w-full h-64 flex flex-center sketch-card mb-4 items-center justify-center'):
                ui.label(current_card[1]).classes('text-3xl font-bold text-center text-slate-800 px-4')
                
                # Show correct/incorrect feedback ONLY after they submit
                if session.is_answered:
                    if session.is_correct:
                        ui.label(f"Correct: {current_card[2]}").classes("text-xl font-bold text-emerald-600 mt-4")
                    else:
                        ui.label(f"Expected: {current_card[2]}").classes("text-xl font-bold text-rose-600 mt-4")
                        ui.label(f"You typed: {session.typed_answer}").classes("text-sm text-slate-400 line-through")
            # PHASE 1: Typing Box
            if not session.is_answered:
                ans_input = ui.input(
                    placeholder="Type answer here...",
                   value=session.typed_answer,
                    on_change=lambda e: setattr(session, "typed_answer", e.value) 
                ).classes("w-full text-center bg-white border-2 border-slate-300 rounded-lg text-slate-900 font-bold py-1 px-3 mb-2").props('input-class="text-center" autofocus')
                ans_input.on('keydown.enter', session.check_answer_wani)
                ui.button("Submit", on_click=session.check_answer_wani).classes("w-full bg-slate-800 text-white font-bold py-2 rounded shadow-none")
           
            # PHASE 2: Grading Buttons
            else:
                ui.label("How difficult was this?").classes("text-xs font-bold text-slate-400 uppercase tracking-widest self-start mb-2 mt-2")
                with ui.row().classes('w-full gap-2 justify-between'):
                    ui.button("Again", on_click=lambda: session.grade_again("wani")).classes("flex-1 bg-rose-100 text-rose-800 font-bold shadow-none border border-rose-300")
                    ui.button("Hard", on_click=lambda: session.grade_hard("wani")).classes("flex-1 bg-amber-100 text-amber-800 font-bold shadow-none border border-amber-300")
                    ui.button("Good", on_click=lambda: session.grade_good("wani")).classes("flex-1 bg-emerald-100 text-emerald-800 font-bold shadow-none border border-emerald-300")
                    ui.button("Easy", on_click=lambda: session.grade_easy("wani")).classes("flex-1 bg-blue-100 text-blue-800 font-bold shadow-none border border-blue-300")
        flashcard_ui()

    #Review (ANKI)

    review_container = ui.column().classes("w-full items-center")
    with review_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        ui.label("Anki Mode (Review)").classes('text-2xl font-bold mb-4 text-slate-800')
        
        @ui.refreshable
        def anki_ui():
            # Check if we are done with the deck
            if not session.anki_queue:
                with ui.column().classes("w-full items-center text-center mt-8"):
                    ui.label("🎉").classes("text-6xl mb-4")
                    ui.label("All done!").classes("text-2xl font-bold text-slate-800")
                return

            current_card = session.anki_queue[0]
            # The interactive flashcard
            with ui.card().classes('w-full h-64 flex flex-center cursor-pointer sketch-card mb-4 items-center justify-center') as card:
                
                # PHASE 1: Question Only
                if not session.is_flipped:
                    ui.label(current_card[1]).classes('text-3xl font-bold text-center text-slate-800 px-4')
                    card.on('click', session.flip_anki)
                else:
                    ui.label(current_card[1]).classes('text-lg font-bold text-center text-slate-400 px-4 mb-4')
                    ui.label(current_card[2]).classes('text-4xl font-bold text-center text-emerald-600 px-4')
            # --- Bottom Controls ---
            
            # If not flipped, show a hint button (or they can just tap the card)
            if not session.is_flipped:
                ui.button("Show Answer", on_click=session.flip_anki).classes("w-full bg-slate-200 text-slate-800 font-bold py-3 rounded-lg shadow-none")
            else:
                ui.label("How difficult was this?").classes("text-xs font-bold text-slate-400 uppercase tracking-widest self-start mb-2")
                with ui.row().classes('w-full gap-2 justify-between'):
                    ui.button("Again", on_click=lambda: session.grade_again("anki")).classes("flex-1 bg-rose-100 text-rose-800 font-bold shadow-none border border-rose-300")
                    ui.button("Hard", on_click=lambda: session.grade_hard("anki")).classes("flex-1 bg-amber-100 text-amber-800 font-bold shadow-none border border-amber-300")
                    ui.button("Good", on_click=lambda: session.grade_good("anki")).classes("flex-1 bg-emerald-100 text-emerald-800 font-bold shadow-none border border-emerald-300")
                    ui.button("Easy", on_click=lambda: session.grade_easy("anki")).classes("flex-1 bg-blue-100 text-blue-800 font-bold shadow-none border border-blue-300")
        
        anki_ui()


    addcards_container = ui.column().classes("w-full")
    with addcards_container:
        ui.button("← Back to deck", on_click=show_decks).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        ui.label("Create New Card").classes('text-2xl font-bold mb-4 text-slate-800')

        with ui.column().classes('w-full sketch-card p-4 gap-4'):
            q_input = ui.input("Question (Front)").classes("w-full bg-slate-50 px-2 py-1")
            a_input = ui.input("Answer (Back)").classes("w-full bg-slate-50 px-2 py-1")

            def submit_card():
                if q_input.value and a_input.value:
                    Card.add_card(q_input.value, a_input.value)
                    session.build_up() # Rebuild the queues so the new card appears in lessons
                    home_ui.refresh()
                    ui.notify("Card added successfully!", type="positive", position="top")

                    q_input.value = ""
                    a_input.value = ""
                    show_decks()
                else:
                    ui.notify("Please fill out both fields.", type="warning", position="top")
            ui.button("Save Card", on_click=submit_card).classes("w-full bg-emerald-500 hover:bg-emerald-600 text-white font-bold py-2 shadow-none")

    decks_container = ui.column().classes("w-full")
    with decks_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        with ui.row().classes("w-full justify-between items-center border-b-2 border-slate-800 pb-2 mb-4"):
            ui.label("Cards").classes("text-xl font-bold text-slate-800")
            ui.button("ADD CARD", on_click=show_addcards).classes("bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-4 rounded shadow-none")

        @ui.refreshable
        def decks_ui():
            # Loop through and display all cards in the deck
            all_cards = Card.learning_cards + Card.reviewing_cards
            
            if not all_cards:
                ui.label("No cards found. Try adding one!").classes("text-slate-500 italic mt-4")
                return
                
            for card in all_cards:
                with ui.row().classes("w-full justify-between py-2 border-b border-slate-200 items-center"):
                    ui.label(card[1]).classes("font-bold text-slate-800")
                    ui.label(card[2]).classes("text-slate-500 text-sm")
        decks_ui()

show_home()

ui.run(title="Ankers Hub", host="172.31.33.59", port=8080, show=False)