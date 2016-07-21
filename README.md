## Force39 - A way to shove words into Bip39 for people who chose their words from a hat.

You've decided to create a [bip39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) HD wallet seed mnemonic but the words you chose aren't valid bip39 for some reason. Sure you can choose any combination of words and program some way to convert those to a proper root key, but that would defeat the purpose of using the bip39 standard, which among other things insists that mnemonics must:

1. Have 3, 6, 9, 12, 15, 18, 21 or 24 words.
2. Use the words from the [bip39 word list](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt).
3. Contain a checksum which works. This one's probably why you're here, because you can't just look at a set of words and decide that they will have a valid checksum.

**The force39 software attempts to reorder a set of given words into a seed that's considered a valid bip39 mnemonic.**

### Disclaimer
Everyone's sick of hearing it but we have to say it again: **DO NOT CHOOSE YOUR WORDS BY HAND**. Humans are fallible and you may choose a predictable pattern. In fact, the reason this tool probably didn't already exist is becuase nobody wants to be the enabler; you shouldn't just pick words, you should have them generated from random [like this website](https://dcpos.github.io/bip39/) in which case they're probably already the bip39 standard. A basic computer can check millions of combinations of words per second, so it's important that you choose the words with dice or put the whole list into a bin and mix it up first, but once you've decided on your words this will help you order them into a valid bip39 seed mnemonic.

### How it works:

Open force39.exe, input your list of words (must be words from the [bip39 wordlist](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)) with a space between each word. Press the "force" button and see the resulting order of words, which will be a valid bip39 seed. If you don't like that seed there are probably lots of combinations that will have a valid checksum, so you can shuffle the input words and try again until you like what you see.

### Limitations & future improvements:
* Words are only validated against the wordlist when you press the force button. In the future, the UI will only allow valid words to be entered. As a result, if you put in a long seed with invalid words (words not included on the bip39 wordlist) then it will stall as it searches for an impossible combination.
* English wordlist only for now.
* Better UI layout to come.
* Tooltips or more directions to come.
* Icons/colours/styling for the GUI to come.
* Document (better comments, make it easier to use CLI) to come.
