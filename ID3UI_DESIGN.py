from nicegui import ui
import sqlite3

# ==========================================
# 1. DATABASE SETUP (Must be at the very top!)
# ==========================================
conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Initial data to seed the database
flashcards_data = [
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
    
    # Insert seed data into SQL
    for card in flashcards_data:
        c.execute("INSERT OR IGNORE INTO flashcards (id, q, a, state, step) VALUES (?, ?, ?, ?, ?)", 
                  (card["id"], card["q"], card["a"], card["state"], card["step"]))

# ==========================================
# 2. STATE & GAMEPLAY MANAGER
# ==========================================
class Card_Manager():
    def __init__(self):
        self.current_index = 0
        self.active_deck = []
        
        # Wani Mode Variables
        self.typed_answer = ""     
        self.is_answered = False   
        self.is_correct = False    
        
        # Anki Mode Variables
        self.is_flipped = False    

        # Load data immediately
        self.load_db()

    def load_db(self):
        c.execute("SELECT * FROM flashcards WHERE state=:state", {"state": "learning"})
        self.learning_cards = c.fetchall()
        
        c.execute("SELECT * FROM flashcards WHERE state=:state", {"state": "reviewing"})
        self.reviewing_cards = c.fetchall()
        
        c.execute("SELECT current_day FROM vars")
        result = c.fetchone()
        self.current_day = result[0]
        
        # Convert SQL rows into a usable list of dictionaries for the UI
        # SQL returns tuples like: (1, 'Question', 'Answer', 'learning', 0)
        self.active_deck = [{"id": row[0], "q": row[1], "a": row[2]} for row in self.learning_cards]

    # --- Wani Mode Logic (Typing) ---
    def check_answer(self):
        if self.current_index >= len(self.active_deck): return
        correct_ans = self.active_deck[self.current_index]["a"].lower()
        self.is_correct = (self.typed_answer.strip().lower() == correct_ans)
        self.is_answered = True
        flashcard_ui.refresh() 

    def next_card(self):
        self.current_index += 1
        self.typed_answer = ""
        self.is_answered = False
        flashcard_ui.refresh() 

    # --- Anki Mode Logic (Flipping) ---
    def flip_anki(self):
        if self.current_index >= len(self.active_deck): return
        self.is_flipped = True
        anki_ui.refresh()

    def next_anki_card(self):
        self.current_index += 1
        self.is_flipped = False
        anki_ui.refresh()

# Initialize the manager (c is already defined above, so this will succeed)
Card = Card_Manager()
#example display
class MockDB:
    def __init__(self):
        # just display number, not a part of the data
        self.learning_count = 15
        self.review_count = 10

db = MockDB()

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

def show_lesson():
    # new words (wanikani)
    home_container.set_visibility(False)
    lesson_container.set_visibility(True)
    review_container.set_visibility(False)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(False)

def show_review():
    home_container.set_visibility(False)
    lesson_container.set_visibility(False)
    review_container.set_visibility(True)
    decks_container.set_visibility(False)
    addcards_container.set_visibility(False)

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

with ui.column().classes("w-full max-w-[480px] mx-auto p-4 mt-4"):
    

    home_container = ui.column().classes("w-full")
    with home_container:
        # Top Bar
        with ui.row().classes("w-full items-center justify-between border-b-2 border-slate-800 pb-2 mb-4"):
            ui.label("ANKERS").classes("text-xl font-bold tracking-widest text-slate-800")

        with ui.row().classes("w-full gap-4 justify-between"):
            # LESSONS CARD
            with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                ui.label(f"Lessons ({len(Card.active_deck)})").classes("font-bold text-slate-800 text-lg")
                ui.icon('local_library', size='3.5rem').classes('text-slate-300 my-2') 
                
                # Routes to the Flashcard mode
                ui.button("Start >", on_click=show_lesson).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")
                ui.button("Options", on_click=lambda: ui.notify("Options")).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")

            # REVIEW CARD
            with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                ui.label(f"Review List").classes("font-bold text-slate-800 text-lg")
                ui.icon('assignment', size='3.5rem').classes('text-slate-300 my-2')
                
                # Routes to the List of Cards mode
                ui.button("Start >", on_click=show_review).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")
                ui.button("Options", on_click=lambda: ui.notify("Options")).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")

        with ui.row().classes("w-full gap-4 justify-between"):

            #CARD LIST
            with ui.column().classes("flex-1 sketch-card p-4 items-center gap-2"):
                ui.label(f"card list").classes("font-bold text-slate-800 text-lg")
                ui.icon('list_alt', size='3.5rem').classes('text-slate-300 my-2')
                ui.button("Start >", on_click=show_decks).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")
                

    #wani FLASHCARD MODE
    lesson_container = ui.column().classes("w-full items-center")
    with lesson_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        ui.label("Wani Mode (Typing)").classes('text-2xl font-bold mb-4 text-slate-800')

        # We make this refreshable so it switches from Input -> Grading seamlessly
        @ui.refreshable
        def flashcard_ui():
            if Card.current_index >= len(Card.active_deck):
                with ui.column().classes("w-full items-center text-center mt-8"):
                    ui.label("🎉").classes("text-6xl mb-4")
                    ui.label("All done!").classes("text-2xl font-bold text-slate-800")
                return
            
            current_card = Card.active_deck[Card.current_index]

            # The Flashcard Window
            with ui.card().classes('w-full h-64 flex flex-center sketch-card mb-4 items-center justify-center'):
                ui.label(current_card["q"]).classes('text-3xl font-bold text-center text-slate-800 px-4')
                
                # Show correct/incorrect feedback ONLY after they submit
                if Card.is_answered:
                    if Card.is_correct:
                        ui.label(f"Correct: {current_card['a']}").classes("text-xl font-bold text-emerald-600 mt-4")
                    else:
                        ui.label(f"Expected: {current_card['a']}").classes("text-xl font-bold text-rose-600 mt-4")
                        ui.label(f"You typed: {Card.typed_answer}").classes("text-sm text-slate-400 line-through")

            # PHASE 1: Typing Box
            if not Card.is_answered:
                ans_input = ui.input(
                    placeholder="Type answer here...",
                    value=Card.typed_answer,
                    # FIX: Attach the typed text to the Card object
                    on_change=lambda e: setattr(Card, "typed_answer", e.value) 
                ).classes("w-full text-center bg-white border-2 border-slate-300 rounded-lg text-slate-900 font-bold py-1 px-3 mb-2").props('input-class="text-center" autofocus')
                
                # Submit when the user presses Enter
                ans_input.on('keydown.enter', Card.check_answer)
                
                ui.button("Submit", on_click=Card.check_answer).classes("w-full bg-slate-800 text-white font-bold py-2 rounded border-2 border-slate-800 shadow-none")
            
            # PHASE 2: Grading Buttons
            else:
                ui.label("How difficult was this?").classes("text-xs font-bold text-slate-400 uppercase tracking-widest self-start mb-2 mt-2")
                with ui.row().classes('w-full gap-2 justify-between'):
                    ui.button("Again", on_click=Card.next_card).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")
                    ui.button("Hard", on_click=Card.next_card).classes("flex-1 bg-amber-100 hover:bg-amber-200 text-amber-800 font-bold shadow-none rounded border border-amber-300")
                    ui.button("Good", on_click=Card.next_card).classes("flex-1 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-bold shadow-none rounded border border-emerald-300")
                    ui.button("Easy", on_click=Card.next_card).classes("flex-1 bg-blue-100 hover:bg-blue-200 text-blue-800 font-bold shadow-none rounded border border-blue-300")

        flashcard_ui()

    #Review (ANKI)

    review_container = ui.column().classes("w-full items-center")
    with review_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        ui.label("Anki Mode (Review)").classes('text-2xl font-bold mb-4 text-slate-800')
        
        @ui.refreshable
        def anki_ui():
            # Check if we are done with the deck
            if Card.current_index >= len(Card.active_deck):
                with ui.column().classes("w-full items-center text-center mt-8"):
                    ui.label("🎉").classes("text-6xl mb-4")
                    ui.label("All done!").classes("text-2xl font-bold text-slate-800")
                return

            current_card = Card.active_deck[Card.current_index]

            # The interactive flashcard
            with ui.card().classes('w-full h-64 flex flex-center cursor-pointer sketch-card mb-4 items-center justify-center') as card:
                
                # PHASE 1: Question Only
                if not Card.is_flipped:
                    ui.label(current_card["q"]).classes('text-3xl font-bold text-center text-slate-800 px-4')
                    # Tapping the card flips it
                    card.on('click', Card.flip_anki)
                
                # PHASE 2: Question + Answer
                else:
                    ui.label(current_card["q"]).classes('text-lg font-bold text-center text-slate-400 px-4 mb-4')
                    ui.label(current_card["a"]).classes('text-4xl font-bold text-center text-emerald-600 px-4')

            # --- Bottom Controls ---
            
            # If not flipped, show a hint button (or they can just tap the card)
            if not Card.is_flipped:
                ui.button("Show Answer", on_click=Card.flip_anki).classes("w-full bg-slate-200 hover:bg-slate-300 text-slate-800 font-bold py-3 rounded-lg border-2 border-slate-300 shadow-none")
            
            # If flipped, show the grading buttons
            else:
                ui.label("How difficult was this?").classes("text-xs font-bold text-slate-400 uppercase tracking-widest self-start mb-2")
                with ui.row().classes('w-full gap-2 justify-between'):
                    ui.button("Again", on_click=Card.next_anki_card).classes("flex-1 bg-rose-100 hover:bg-rose-200 text-rose-800 font-bold shadow-none rounded border border-rose-300")
                    ui.button("Hard", on_click=Card.next_anki_card).classes("flex-1 bg-amber-100 hover:bg-amber-200 text-amber-800 font-bold shadow-none rounded border border-amber-300")
                    ui.button("Good", on_click=Card.next_anki_card).classes("flex-1 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 font-bold shadow-none rounded border border-emerald-300")
                    ui.button("Easy", on_click=Card.next_anki_card).classes("flex-1 bg-blue-100 hover:bg-blue-200 text-blue-800 font-bold shadow-none rounded border border-blue-300")

        anki_ui()

    addcards_container = ui.column().classes("w-full")
    with addcards_container:
        ui.button("← Back to deck", on_click=show_decks).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")


    decks_container = ui.column().classes("w-full")
    with decks_container:
        ui.button("← Back to Hub", on_click=show_home).props("flat dense").classes("text-slate-500 self-start mb-4 font-bold")
        with ui.row().classes("w-full justify-between items-center border-b-2 border-slate-800 pb-2 mb-4"):
            ui.label("Cards").classes("text-xl font-bold text-slate-800")
            ui.button("ADD CARD", on_click=lambda: ui.notify("Add card clicked")).classes("bg-blue-500 hover:bg-blue-600 text-white font-bold py-1 px-4 rounded shadow-none")

            # Loop through and display all cards in the deck
            for c in Card.active_deck:
                with ui.row().classes("w-full justify-between py-2 border-b border-slate-200 items-center"):
                    ui.label(c["q"]).classes("font-bold text-slate-800")
                    ui.label(c["a"]).classes("text-slate-500 text-sm")


show_home()

ui.run(title="Ankers Hub", host="192.168.1.49", port=8080, show=False)