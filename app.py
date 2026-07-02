import json
import os
from typing import List, Dict, Any, Optional
from nicegui import ui

# Local database path using a JSON file
DB_FILE = "cards_db.json"

DEFAULT_CARDS = [
    {"id": "1", "prompt": "おはようございます", "answer": "Good morning", "state": "learning", "step": 0, "history": [], "next_review_day": 0},
    {"id": "2", "prompt": "こんにちは", "answer": "Good afternoon", "state": "learning", "step": 0, "history": [], "next_review_day": 0},
    {"id": "3", "prompt": "こんばんは", "answer": "Good evening", "state": "learning", "step": 0, "history": [], "next_review_day": 0},
    {"id": "4", "prompt": "はじめまして", "answer": "Nice to meet you", "state": "learning", "step": 0, "history": [], "next_review_day": 0},
    {"id": "5", "prompt": "ありがとうございます", "answer": "Thank you", "state": "learning", "step": 0, "history": [], "next_review_day": 0},
]

class CardManager:
    def __init__(self):
        self.cards: List[Dict[str, Any]] = []
        self.current_day = 0
        self.load_db()

    def load_db(self):
        # Load database from file if it exists, otherwise initialize default cards
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.cards = data.get("cards", DEFAULT_CARDS)
                    self.current_day = data.get("current_day", 0)
            except Exception:
                self.cards = DEFAULT_CARDS
                self.current_day = 0
        else:
            self.cards = DEFAULT_CARDS
            self.current_day = 0
            self.save_db()

    def save_db(self):
        # Save the current state of cards and current day to the database file
        try:
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump({"cards": self.cards, "current_day": self.current_day}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error: save failed {e}")

    def add_card(self, prompt: str, answer: str) -> str:
        new_id = str(max([int(c["id"]) for c in self.cards] + [0]) + 1)
        card = {
            "id": new_id,
            "prompt": prompt.strip(),
            "answer": answer.strip(),
            "state": "learning",
            "step": 0,
            "history": [],
            "next_review_day": self.current_day
        }
        self.cards.append(card)
        self.save_db()
        return new_id

    def delete_card(self, card_id: str):
        self.cards = [c for c in self.cards if c["id"] != card_id]
        self.save_db()

# Initialize the global card manager instance
db = CardManager()

class SessionState:
    def __init__(self):
        self.active_queue: List[str] = []
        self.current_card_id: Optional[str] = None
        self.typed_answer: str = ""
        self.ui_stage: str = "input"  # input or feedback
        self.auto_grade: Optional[str] = None
        self.feedback_msg: str = ""
        self.is_correct: bool = False
        
        # Initialize session queue
        self.build_queue()

    def build_queue(self):
        # Active queue consists of cards in learning state and review cards due today
        queue = []
        for c in db.cards:
            if c["state"] == "learning":
                queue.append(c["id"])
            elif c["state"] == "review" and c.get("next_review_day", 0) <= db.current_day:
                queue.append(c["id"])
        # Clear recent session history of cards to start fresh
        for cid in queue:
            card = self.get_card(cid)
            if card:
                card["history"] = []
        self.active_queue = queue
        self.next_card()

    def get_card(self, card_id: str) -> Optional[Dict[str, Any]]:
        for c in db.cards:
            if c["id"] == card_id:
                return c
        return None

    def next_card(self):
        if self.active_queue:
            self.current_card_id = self.active_queue[0]
            self.typed_answer = ""
            self.ui_stage = "input"
            self.auto_grade = None
            self.feedback_msg = ""
        else:
            self.current_card_id = None

    def insert_queue(self, card_id: str, offset: int):
        # Insert flashcard at a specific offset in the review queue
        if card_id in self.active_queue:
            self.active_queue.remove(card_id)
        if offset >= len(self.active_queue):
            self.active_queue.append(card_id)
        else:
            self.active_queue.insert(offset, card_id)

    def submit_typed_answer(self):
        card = self.get_card(self.current_card_id)
        if not card:
            return

        typed = self.typed_answer.strip().lower()
        actual = card["answer"].strip().lower()
        
        # Strip basic punctuation to allow for minor input variances
        for char in [".", ",", "?", "!"]:
            typed = typed.replace(char, "")
            actual = actual.replace(char, "")

        self.is_correct = (typed == actual)
        
        # Record response history
        if "history" not in card:
            card["history"] = []
        card["history"].append(self.is_correct)
        db.save_db()

        # Determine automatic grade recommendation based on response history
        history = card["history"]
        if self.is_correct:
            # Recommend 'Easy' if the card has been answered correctly 3 times consecutively
            if len(history) >= 3 and all(history[-3:]):
                self.auto_grade = "Easy"
            else:
                self.auto_grade = "Good"
            self.feedback_msg = "Correct!"
        else:
            # Count consecutive incorrect attempts to suggest appropriate scheduling action
            consec_wrongs = 0
            for val in reversed(history):
                if not val:
                    consec_wrongs += 1
                else:
                    break
            
            if consec_wrongs == 1:
                self.auto_grade = "Good"
            elif consec_wrongs == 2:
                self.auto_grade = "Hard"
            else:
                self.auto_grade = "Again"
            self.feedback_msg = f"Incorrect. Expected: \"{card['answer']}\""

        self.ui_stage = "feedback"

    def apply_action(self, grade: str):
        if not self.current_card_id:
            return
        
        card = self.get_card(self.current_card_id)
        if not card:
            return

        state = card["state"]
        step = card.get("step", 0)
        
        # Update scheduling interval based on user/system difficulty rating
        if grade == "Again":
            # Reset card progress to initial learning step and queue it soon
            card["state"] = "learning"
            card["step"] = 0
            card["history"] = []
            self.insert_queue(self.current_card_id, 3)
        elif grade == "Hard":
            if state == "learning":
                self.insert_queue(self.current_card_id, 5)
            else:
                card["next_review_day"] = db.current_day + 1
                if self.current_card_id in self.active_queue:
                    self.active_queue.remove(self.current_card_id)
        elif grade == "Good":
            if state == "learning":
                if step < 2:
                    card["step"] += 1
                    offset = 4 if step == 0 else 3
                    self.insert_queue(self.current_card_id, offset)
                else:
                    # Card graduates to review state
                    card["state"] = "review"
                    card["step"] = 0
                    card["history"] = []
                    card["next_review_day"] = db.current_day + 3
                    if self.current_card_id in self.active_queue:
                        self.active_queue.remove(self.current_card_id)
            else:
                card["next_review_day"] = db.current_day + 3
                if self.current_card_id in self.active_queue:
                    self.active_queue.remove(self.current_card_id)
        elif grade == "Easy":
            card["state"] = "review"
            card["step"] = 0
            card["history"] = []
            if state == "learning":
                self.insert_queue(self.current_card_id, 8)
                card["next_review_day"] = db.current_day + 7
            else:
                card["next_review_day"] = db.current_day + 7
                if self.current_card_id in self.active_queue:
                    self.active_queue.remove(self.current_card_id)

        db.save_db()
        self.next_card()

    def advance_day(self):
        db.current_day += 1
        db.save_db()
        self.build_queue()

# Initialize state manager for current user session
state = SessionState()

# UI Layout and Styling (to make it look decent)
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

# Main app layout setup
with ui.column().classes("w-full items-center justify-center p-4 min-h-screen max-w-[480px] mx-auto text-slate-900 pb-24"):
    
    # Header section
    with ui.row().classes("w-full items-center justify-between mb-4 px-2"):
        with ui.column().classes("gap-0"):
            ui.label("Ankers").classes("text-2xl font-bold text-slate-900 tracking-tight")
            ui.label("Spaced Repetition Flashcards").classes("text-xs text-slate-500")
        
        # Day indicator and advancement controls
        with ui.row().classes("items-center gap-2"):
            @ui.refreshable
            def day_view():
                ui.label(f"Day {db.current_day}").classes("text-xs font-semibold px-2 py-1 bg-slate-100 text-slate-700 rounded")
            day_view()
            ui.button("Next Day", on_click=lambda: [state.advance_day(), refresh_all()]).props("flat dense").classes("text-xs capitalize font-medium text-indigo-600 hover:text-indigo-700")

    # Queue statistics row
    @ui.refreshable
    def stats_view():
        learning_count = sum(1 for c in db.cards if c["state"] == "learning")
        review_due = sum(1 for c in db.cards if c["state"] == "review" and c.get("next_review_day", 0) <= db.current_day)
        review_future = sum(1 for c in db.cards if c["state"] == "review" and c.get("next_review_day", 0) > db.current_day)
        
        with ui.row().classes("w-full justify-between px-3 py-2 bg-white border border-slate-200 rounded-lg mb-4 text-xs text-slate-600"):
            ui.label(f"Learning: {learning_count}").classes("text-indigo-600 font-medium")
            ui.label(f"Due: {review_due}").classes("text-amber-600 font-medium")
            ui.label(f"Scheduled: {review_future}").classes("text-emerald-600 font-medium")
            ui.label(f"Queue: {len(state.active_queue)}").classes("text-purple-600 font-semibold")

    stats_view()

    # Flashcard view container
    @ui.refreshable
    def flashcard_view():
        if not state.current_card_id:
            # Active queue is empty
            with ui.column().classes("w-full card-panel p-8 items-center text-center gap-4 my-2"):
                ui.label("🎉").classes("text-4xl my-2")
                ui.label("yay all done!!").classes("text-lg font-semibold text-slate-900")
                ui.label("There are no reviews left for today. You can advance the day or add new cards below.").classes("text-xs text-slate-500 max-w-[320px]")
                ui.button("Advance to Next Day", on_click=lambda: [state.advance_day(), refresh_all()]).classes("w-full mt-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm py-2 capitalize").props("flat=false")
            return

        card = state.get_card(state.current_card_id)
        if not card:
            return

        # Determine card state and tag details
        is_rev = card["state"] == "review"
        state_badge = "Review" if is_rev else f"Learn Step {card.get('step', 0) + 1}/3"
        badge_bg = "bg-amber-50 text-amber-700" if is_rev else "bg-indigo-50 text-indigo-700"

        with ui.column().classes("w-full card-panel p-6 items-center gap-4 my-2"):
            # Header status indicator row
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(state_badge).classes(f"text-[10px] px-2.5 py-0.5 rounded font-bold uppercase tracking-wider {badge_bg}")
                ui.label(f"Queue Pos: 1/{len(state.active_queue)}").classes("text-[11px] text-slate-400 font-medium")

            # Word prompt
            ui.label(card["prompt"]).classes("text-4xl font-semibold text-slate-900 text-center tracking-wide my-8")

            # Input phase
            if state.ui_stage == "input":
                ans_input = ui.input(
                    placeholder="Type answer here...",
                    value=state.typed_answer,
                    on_change=lambda e: setattr(state, "typed_answer", e.value)
                ).classes("w-full text-center bg-slate-50 border border-slate-200 rounded-lg text-slate-900 font-medium py-1 px-3 focus:outline-none focus:border-indigo-500").props('input-class="text-center" autofocus')
                
                # Submit when enter is pressed or button is clicked
                ans_input.on("keydown.enter", lambda: [state.submit_typed_answer(), refresh_all()])
                
                ui.button("Submit Answer", on_click=lambda: [state.submit_typed_answer(), refresh_all()]).classes("w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-sm py-2 capitalize")
            
            # Feedback and manual rating phase
            else:
                feedback_class = "text-emerald-600 text-lg font-semibold" if state.is_correct else "text-rose-600 text-lg font-semibold"
                with ui.column().classes("w-full items-center text-center gap-2"):
                    ui.label(state.feedback_msg).classes(feedback_class)
                    if not state.is_correct:
                        ui.label(f"Your answer: \"{state.typed_answer}\"").classes("text-xs text-slate-400 line-through")

                # Manual grading decision buttons
                ui.label("Difficulty Rating").classes("text-xs text-slate-400 font-semibold uppercase tracking-wider mt-4 self-start")
                
                # Button colors and highlight builder
                def btn_class(g: str) -> str:
                    base = "flex-1 text-[11px] py-1.5 rounded-lg font-semibold transition-all border "
                    if state.auto_grade == g:
                        return base + "bg-indigo-600 border-indigo-600 text-white shadow-sm"
                    else:
                        return base + "bg-white border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50"

                with ui.row().classes("w-full gap-2 justify-between mt-1"):
                    ui.button("Again", on_click=lambda: [state.apply_action("Again"), refresh_all()]).classes(btn_class("Again")).props("flat")
                    ui.button("Hard", on_click=lambda: [state.apply_action("Hard"), refresh_all()]).classes(btn_class("Hard")).props("flat")
                    ui.button("Good", on_click=lambda: [state.apply_action("Good"), refresh_all()]).classes(btn_class("Good")).props("flat")
                    ui.button("Easy", on_click=lambda: [state.apply_action("Easy"), refresh_all()]).classes(btn_class("Easy")).props("flat")

                # Confirm submission
                confirm_btn = ui.button("Confirm & Next (Enter)", on_click=lambda: [state.apply_action(state.auto_grade), refresh_all()]).classes("w-full mt-4 bg-slate-100 border border-slate-200 hover:bg-slate-200 rounded-lg font-semibold text-xs text-indigo-600 py-2 capitalize")

    flashcard_view()

    # Management Panel: Deck database manager
    with ui.expansion("Manage Deck", icon="inventory_2").classes("w-full card-panel mt-6 text-slate-700 font-semibold").props("header-class=\"text-sm text-slate-700\""):
        with ui.column().classes("w-full p-4 gap-4"):
            # Add flashcard form
            ui.label("Add New Flashcard").classes("text-xs font-semibold text-slate-400 uppercase tracking-wider")
            with ui.row().classes("w-full gap-2 items-center"):
                prompt_input = ui.input(placeholder="japanese (Q)").classes("flex-1 bg-white border border-slate-200 rounded-lg px-2 text-xs text-slate-900")
                answer_input = ui.input(placeholder="english (A)").classes("flex-1 bg-white border border-slate-200 rounded-lg px-2 text-xs text-slate-900")
                
                def add_and_clear():
                    p = prompt_input.value
                    a = answer_input.value
                    if p and a:
                        db.add_card(p, a)
                        prompt_input.value = ""
                        answer_input.value = ""
                        state.build_queue()
                        refresh_all()
                        ui.notify("Card added to deck!", type="positive", position="top")
                
                ui.button("Add Card", on_click=add_and_clear).classes("bg-indigo-600 hover:bg-indigo-700 rounded-lg text-xs font-semibold px-4 py-1 text-white capitalize")

            # Active cards list
            ui.label("Deck List").classes("text-xs font-semibold text-slate-400 uppercase tracking-wider mt-2")
            
            @ui.refreshable
            def cards_list_view():
                with ui.column().classes("w-full gap-2 max-h-[250px] overflow-y-auto pr-1"):
                    for c in db.cards:
                        with ui.row().classes("w-full justify-between items-center p-2 rounded-lg bg-slate-50 border border-slate-200 text-xs"):
                            with ui.column().classes("gap-0.5"):
                                ui.label(f"{c['prompt']} → {c['answer']}").classes("font-semibold text-slate-900")
                                status_lbl = "Review Mode" if c["state"] == "review" else f"Learning (Step {c.get('step', 0) + 1}/3)"
                                ui.label(status_lbl).classes("text-[10px] text-slate-400 font-medium")
                            
                            def delete_wrapper(cid=c["id"]):
                                db.delete_card(cid)
                                state.build_queue()
                                refresh_all()
                                ui.notify("Card removed from deck.", type="warning", position="top")
                            
                            ui.button(icon="delete", on_click=delete_wrapper).props("flat dense color=negative").classes("text-xs")

            cards_list_view()

def refresh_all():
    day_view.refresh()
    stats_view.refresh()
    flashcard_view.refresh()
    cards_list_view.refresh()

# Global key listener for Enter press
def handle_key(e):
    if e.action.keydown and e.key == 'Enter':
        if state.ui_stage == "feedback" and state.auto_grade:
            state.apply_action(state.auto_grade)
            refresh_all()

ui.keyboard(on_key=handle_key)

# Run the app locally, optimized for webapp
ui.run(title="Ankers", host="127.0.0.1", port=8080, show=False)

