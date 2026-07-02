from tkinter import *
from random import randint


root = Tk()
root.title('Wanikani typeshii - 日本語 flashcards')
root.geometry("550x410")

word = [
    (("おはようございます"), ("Good morning")),
    (("こんにちは"), ("Good afternoon")),
    (("こんばんは"), ("Good evening")),
    (("はじめまして"), ("Nice to meet you")),
]
count = len(word)

def next():
    randWord = randint(0,count-1)
    global randWord

    jpnWord.config(text=word[randWord][0])

    myEntry.delete(0, END)
    ansLabel.config(text="")

def answer():
    if myEntry.get() == word[randWord][1]:
        ansLabel.config(text=f"correct! {word[randWord][0]} is {myEntry.get()}")
    else:
        ansLabel.config(text=f"wrong! {word[randWord][0]} is not {myEntry.get()}")

jpnWord = Label(root, text="", font=("Arial", 36))
jpnWord.pack(pady=50)

ansLabel = Label(root, text="")
ansLabel.pack(pady=20)

myEntry = Entry(root, font=("Arial", 18))
myEntry.pack(pady=20)

#buttons

buttonFrame = Frame(root)
buttonFrame.pack(pady=20)

ansButton = Button(buttonFrame, text="answer", command=answer)
ansButton.grid(row=0,column=0, padx=20)

nextButton = Button(buttonFrame, text="Next", command=next)
nextButton.grid(row=0,column=1,)





next()


root.mainloop()
