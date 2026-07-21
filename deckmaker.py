import sqlite3

con = sqlite3.connect("wanker.db")
#database connection to wanker.db
#declared on each command associated with db

cur = con.cursor()
#cursor object for "con", tutorial.db
#all commands calling cur will call tutorial.db implicitly


flashcards_def = [
    {"id": 1, "q": "What is the capital of Japan?", "a": "Tokyo", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0},
    {"id": 2, "q": "What is the Japanese word for 'Thank you'?", "a": "Arigatou", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0},
    {"id": 3, "q": "What is $5 \\times 5$?", "a": "25", "state": "learning", "step": 0, "days_till_review": 0, "review_count": 0}
]
#test flashcard deck to demonstrate function. order of keys in dictonaries is
#id, question, answer, state, step, days till review, and review count

deckname = "deck1"
#variable to name deck

def createdeck(deckname):
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS
        {deckname}(id INTEGER,
        question TEXT,
        answer TEXT,
        state TEXT,
        step INTEGER,
        days_till_review INTEGER,
        review_count INTEGER)""")
#function that creates deck based on deckname variable. Prolly wanna make input prompt that changes deckname when making card maker layout
createdeck(deckname)

def createcard(deckname, q, a):
    deckIDs = cur.execute(f"SELECT id from {deckname}")
    idvalue = len(deckIDs.fetchall()) + 1
    cur.execute(f"INSERT INTO {deckname} VALUES(?, ?, ?, 'learning', 0, 0, 0)", (idvalue, q, a))
    con.commit()
#function to create card and add to selected deck. Ideally the input prompts have some sort of check to confirm uploadable data types.
#The first input variable is the name of the deck. Each subsequent variable is for a key in the dictionary. Note that they're being
#made into a database.

def upload(deckname):
    for row in cur.execute(f"SELECT question, answer, state, step, days_till_review, review_count FROM {deckname}"):
        newID = len(flashcards_def) + 1
        flashcards_def.append({"id": newID, "q": row[0], "a": [1], "state": row[2], "step": row[3], "days_till_review": row[4], "review_count": row[5]})
#FOR UPLOADING TO CARD POOL. Run this function with table name in database.


