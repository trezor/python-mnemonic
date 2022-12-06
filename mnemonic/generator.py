import random
import sys
from mnemonic import Mnemonic

# This prevents IDE from creating a cache file
sys.dont_write_bytecode = True

class Generator:
    def __init__(self, entropy_size: int, chosen_theme: str, entropy):
        # Pick "finances" as default, if no theme is given
        chosen_theme = (chosen_theme if chosen_theme is not None else "finances")
        self.m = Mnemonic(chosen_theme)
        self.phrase_len = len(self.m.words_dictionary["FILLING_ORDER"])
        # Pick random if the entropy input is none
        entropy_bits = (entropy if entropy is not None else bytearray(
            [random.getrandbits(8) for _ in range(entropy_size//8)]))
        self.phrase = self.m.to_mnemonic(entropy_bits).split()

    def show_phrases(self) -> list[str]:
        """
            This method prints the generated phrases and returns the phrases
        Returns
        -------
        str
            This is the returned phrases generated as a string variable
        """
        for i in range(len(self.phrase)):
            print(self.phrase[i][0:2], end="")
        print("")
        for i in range(len(self.phrase)//self.phrase_len):
            print(" ".join(self.phrase[self.phrase_len*i:self.phrase_len*(i+1)]))
        return self.phrase


if len(sys.argv) == 1:
    theme = "finances"
    number_phrases = 8
elif len(sys.argv) == 2:
    if sys.argv[1].isdigit():
        number_phrases = int(sys.argv[1])
        theme = "finances"
    else:
        theme = sys.argv[1]
        number_phrases = 8
else:
    theme = sys.argv[1] if not sys.argv[1].isdigit() else sys.argv[2]
    number_phrases = int(sys.argv[1]) if sys.argv[1].isdigit() else int(sys.argv[2])

g = Generator(number_phrases*32, theme, None)

if __name__ == "__main__":
    g.show_phrases()
