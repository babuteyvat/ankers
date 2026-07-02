# Ankers - SRS

## How to run 

First, make sure you install NiceGUI:
```bash
pip install nicegui
```

Then, start the application:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:8080` to start studying.
We also need to expose this shitty port if you wanna access from phone.
---

## How it works (the scheduler)

The app automatically schedules cards based on how well you remember them. It manages cards in two main phases: **Learning** and **Review**.

### 1. The learning phase
Every new card starts in the **Learning** phase. To graduate a card to the **Review** phase, you need to get it correct multiple times (representing "learning steps"):
- The card requires 3 learning steps (Step 1, Step 2, and Step 3).
- Getting a card correct advances it by one step. Getting it incorrect resets its progress.

### 2. Auto-Gradingsuggestions
When you type an answer, the app strips out punctuation (like `.` or `?`) and compares it to the correct answer. Once submitted, it highlights a recommended rating based on your history with that card in the current session:
- **Easy** is suggested if you get the card correct 3 times in a row.
- **Good** is suggested for your first mistake, or for general correct answers.
- **Hard** is suggested if you fail the card twice in a row.
- **Again** is suggested if you fail the card 3 or more times or if you're `bryan`.

### 3. Review intervals (What the buttons do)

After seeing the feedback, you can accept the suggested rating or choose one of the four buttons. This determines when you'll see the card next:

* **Again**: Resets the card back to the start of the learning phase (Step 1). It is re-inserted into the active queue to show up again in **3 cards**.
* **Hard**: 
  - *If learning:* The card is re-inserted into the active queue to show up in **5 cards**.
  - *If in review:* The card is scheduled to be reviewed again tomorrow (**1 day**).
* **Good**:
  - *If learning:* Advances the card's learning step. If it's already on Step 3, it graduates to the **Review** phase and is scheduled for review in **3 days**. Otherwise, it shows up again in **3 to 4 cards**.
  - *If in review:* Schedules the card to be reviewed in **3 days**.
* **Easy**: Graduates the card directly to the **Review** phase (if it wasn't already) and schedules it for review in **7 days**.

### 4. Review Phase & simulating days
Once a card is scheduled for a future day, it is removed from your current queue. 
- You can simulate dayse by clicking **Next Day** at the top right. 
- When the simulated day matches or passes a card's scheduled review day, it is added back to your active queue for review.