# main.py
from nicegui import ui
from pages import home, study, review, deck_maker

@ui.page('/')
def index():
    home.create()

@ui.page('/study')
def study_route():
    study.create()

@ui.page('/review')
def review_route():
    review.create()

@ui.page('/deck-maker')
def deck_route():
    deck_maker.create()

ui.run(title='Ankers')