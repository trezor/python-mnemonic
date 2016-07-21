from Tkinter import *
import itertools
import os
import binascii
import mnemonic
import random


class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        self.inputa_label = Label(frame, text="Input a list of bip39 words with spaces between them:")
        self.inputa_label.pack()
        self.entry_seed = Entry(frame, bd=3, width=80)
        self.entry_seed.pack()
        self.button_shuffle = Button(frame, text="Shuffle words", command=self.mix_words)
        self.button_shuffle.pack()
        self.result_description = Label(frame, text="In this order, your words are a valid bip39 seed:")
        self.result_description.pack()
        self.result_label = Label(frame, text="")
        self.result_label.pack()
        self.slogan = Button(frame,
                             text="Force valid bip39 order",
                             command=self.main_validate)
        self.slogan.pack()
        self.button_quit = Button(frame,
                                  text="QUIT", fg="red",
                                  command=frame.quit)

        self.button_quit.pack()

    def main_validate(self):
        """Checks for a valid bip39 seed from the given list of words."""
        self.result_label['text'] = ''
        seed_input = []
        seed_input = self.entry_seed.get().split()
        m = mnemonic.Mnemonic('english')
        for subset in itertools.permutations(seed_input, len(seed_input)):
            if len(subset) == len(seed_input):
                if m.check(' '.join(subset)):
                    if subset != seed_input:
                        self.result_label['text'] = ' '.join(subset)
                    else:
                        self.result_label['text'] = "There was a problem with the words you gave, maybe they are not on the bip39 word list or the number of words does not work."
                    break  # found a valid one, stop looking.

    def mix_words(self):
        """Shuffles the words in the entry field."""
        seed_input = []
        seed_input = self.entry_seed.get().split()
        # print(seed_input)
        shuffled = random.sample(seed_input, len(seed_input))
        # print(shuffled)
        self.entry_seed.delete(0, END)
        self.entry_seed.insert(0, " ".join(shuffled))


root = Tk()
root.title("Force39")
app = App(root)
root.mainloop()
