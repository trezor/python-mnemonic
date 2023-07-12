# Formosa

[Formosa](https://formosadefense.com/) is a password format that maximizes the ratio of password strength to user effort.

The password generation process consists of mapping input into meaningful mnemonic sentences, that are, then, condensed into the password.

This is an improvement on the BIP-0039 method — which provides sequences of semantically and syntactically disconnected words as passphrases — because it uses meaningful phrases with a certain theme.

## Why you should use this
- **Strong and memorable passwords:** the sentences below are an example of mnemonics generated by our algorithm.

  *Sherlock Holmes needs a metal circlet from Aphrodite aquarium.
  Little Red Ridding Hood obtains a mesh bracelet in Dracula's hospital.*
  
  The first two letters of each clause structure element form the following password:
   
  *shnemecifrapaqliobmebrdrho*
 
  Now, take a look at a hexadecimal password a regular generator might give you:
  
  *428e916294213680*

  Pretty hard to remember, right? And it's still weaker than the one our generator created! Hence, by using our method, you'll be guaranteed to get both strong and easy-to-recall passwords for all your protected data.

- **Self-checking passwords:** the check-sum technology embedded in the password helps you detect typos.
- **0 adoption barrier:** any legacy BIP39 user can keep their keys and addresses and convert their seed to any Formosa theme. Backwards conversion to original BIP39 is set before KDF proper, so resulting keys end up being the same.
## Motivation

For reasons beyond the scope of this work, the use of passwords is a very popular and widely employed component of information security systems. At the same time, in general, as with information security, human components tend to be the ones most susceptible to failure.

According to a [survey](https://press.avast.com/83-of-americans-are-using-weak-passwords) conducted by Avast in 2019, 83% of Americans create weak passwords to protect their online data, and over 50% use the same passphrase over multiple accounts.

Moreover, as reported by [Google](https://storage.googleapis.com/gweb-uniblog-publish-prod/documents/PasswordCheckup-HarrisPoll-InfographicFINAL.pdf), 4 in 10 Americans have had their personal data stolen. In light of these alarming facts, we aimed at developing a password generator algorithm that creates both secure and memorable passwords.

It is intuitively easier to recall meaningful phrases than it is to remember a sequence of random terms; in fact, that is the fundamental principle behind popular memorization techniques, such as the [PAO system](https://www.wikiwand.com/en/Mnemonic_peg_system) and the [method of loci](https://www.wikiwand.com/en/Method_of_loci), employed by sucessful mental athletes worldwide.

## Installation

### For non-programmers 
#### To download a Windows executable (may not work on all systems)
1. Go to the [executables folder on the project's main page](https://gitlab.com/t3-infosec/formosa/-/tree/main/executables)
2. Click on the Windows version
3. Click on the download button at the center of the screen
4.  Click twice on the downloaded file to run
#### To download a Linux executable (may not work on all systems)
1. Go to the [executables folder on the project's main page](https://gitlab.com/t3-infosec/formosa/-/tree/main/executables)
2. Click on the Linux version
3. Click on the download button at the center of the screen
4.  Click on the downloaded file to run
### For tech-savvy people
Clone the release branch by running the following command on the terminal:
```console
git clone https://gitlab.com/t3-infosec/formosa.git
```
#### To run graphical user interface on your own environment
1. Navigate to the "mnemonic" folder
2. Run the GUI_qt.py file on Python

#### To run source code on terminal
1. In your local repository, navigate to the "mnemonic" folder
2. On Python, run the following command:

```console
python3 mnemonic.py theme cryptographic_strength
```
This will generate eight finances-themed mnemonic sentences and its derived password by default. To change the number of phrases and/or theme, use the following arguments. Available themes include:

- role_play
- sci-fi
- copy_left (fairy tales and mythology)
- tourism
- finances

The cryptographic strength argument refers to how hard it is to crack the password by brute-force. It is a multiple of 32 between 32 and 256. Thumb rule is 64 is good for non critical password and 128 is good enough for most applications. In fact 128 bits of entropy is, in fact, the most used standard for cryptocurrency seeds, as deemed adequate by the author. From 160 to 256 is tin-foil hat territory.

**Command**
```console
python3 mnemonic.py sci-fi 160
```
**Output**
```
asbuamwelineursamaincltirefrbewrexplexfogrslsuclgropioemovgo
assistant buy amalgam welder linguist nebula
uranian sabotage martian injector clone titan
reptilian freeze beta_particle wrench explorer planet_ring
explorer forbid graphene sledge_hammer submariner cluster
green_man operate ion emitter overmind goldilock_zone
```

**Command**
```console
python3 mnemonic.py copy_left 96
```

**Output**
```
lideoagrurbarorecrpielgrlepuicgehaki
little_red_riding_hood describe oak gravestone ursula bakery
robinson_crusoe reach crystal pickaxe eloi graveyard
legolas pull icy gem hades kitchen
```


#### To find executables in the source code
1. In your local repo, navigate to the "Download Apps" folder
2. Choose your operating system
3. Choose the version of your operating system
4. Run the executable


#### To build your own executable on Windows (may not work on certain systems)
1. Make sure you have Python, Tkinter, base58, and PyInstaller installed.
2. Navigate to the "mnemonic" folder
3. Enter the following command:

```console
pyinstaller --paths C:\Windows\System32\downlevel --paths C:\Windows\SysWOW64\downlevel --onefile -w --add-data 'themes\copy_left\;themes\copy_left\' --add-data 'themes\finances\;themes\finances\' --add-data 'themes\role_play\;themes\role_play\' --add-data 'themes\sci-fi\;themes\sci-fi\' --add-data 'themes\tourism\*;themes\tourism\' GUI_qt.py
```
If the former doesn't work, try this:

```console
python -m PyInstaller --paths C:\Windows\System32\downlevel --paths C:\Windows\SysWOW64\downlevel --onefile -w --add-data 'themes\copy_left\;themes\copy_left\' --add-data 'themes\finances\;themes\finances\' --add-data 'themes\role_play\;themes\role_play\' --add-data 'themes\sci-fi\;themes\sci-fi\' --add-data 'themes\tourism\*;themes\tourism\' GUI_qt.py
```
4. Two new directories will be created: build and dist. The build folder can be deleted, while dist will contain your executable.

**Note:** the executable will only work on computers with the same operating system and version as the one it was built in.

#### To build your own executable on Linux (may not work on certain systems)
1. Make sure you have Python, Tkinter, base58, and PyInstaller installed.
2. Navigate to the "mnemonic" folder
3. Enter the following command:
```
python3 -m PyInstaller --onefile \
  --add-data 'themes/copy_left/*:themes/copy_left/' \
  --add-data 'themes/finances/*:themes/finances/' \
  --add-data 'themes/role_play/*:themes/role_play/' \
  --add-data 'themes/sci-fi/*:themes/sci-fi/' \
  --add-data 'themes/tourism/*:themes/tourism/' \
  -w GUI_qt.py
```
4. Two new directories will be created: build and dist. The build folder can be deleted, while dist will contain your executable.

**Note:** the executable will only work on computers with the same operating system and version as the one it was built in.

## How to use the passphrases
After running the program, you will have a strong password and a number of strings to help you remember it. To turn them into actual phrases, you will have to add the necessary prepositions and conjugate the verbs accordingly.

For example, here is the output for a password of one mnemonic sentence in the theme of copyleft:

```
phantom_of_the_opera suggest diamond feather cinderella court
```
To make the mnemonic sentence easier to remember, you could memorize it as one of the following:
- The Phantom of The Opera suggests a diamond feather to Cinderella at the court
- The Phantom of The Opera suggests a diamond feather at Cinderella's court

Use your imagination to make it even more memorable; visualize the **Phantom** in an elegant suit, bowing to **Cinderella** as he offers her a **diamond feather**. They at a shadowed **court** in the palace, but the sparkle of her glass slippers cathches his eye, and he **suggests** the diamond feather would go well with it. 

In the roleplay theme, you could also get a passphrase similar to this:

```
emasgobamaga
emissary ask_for golden bag maiden garden
```
You could memorize one of the following:
- The emissary asks for the golden bag to the maiden in the garden
- The emissary asks for a golden bag in the maiden's garden

Here's another example in the finances theme:
```
spacmacobali
speculator accept marginal compound_interest banker liberland
```
A possible sentence is:
- A speculator accepts a marginal compound interest from the banker at Liberland

### How many passphrases do I need?
At least two, preferably four.


## Explanation for nerds

An input **array** of 32 ⋅ n bits is hashed by sha256; from the resulting digest, the first n bits are appended to the input. This extended input is divided into **subarrays** of 33 bits, each determining a **sentence**. In each **sentence** (all having the same syntatic structure), its 33 bits are then subdivided into a fixed number of **chunks**, typically with 5 or 6 bits. These, in turn, specify the words or expressions -- henceforwards **terms** -- that constitute the clause synctactic elements (subject, verb, complement, and adjunct).

At each sentence, each **clause syntactic element** is determined in a fixed order for each given **theme**. The first **chunk** specifies an element from an unrestricted list of possibilities. From the second **chunk** onwards, each list of possible **terms** is given by one previously determined **term**.

For example, say the first chunk determines the verb and the second chunk determines the subject; if the first chunk maps to "to meow", the second chunk elicits another term from a sublist of subjects semantically fitting to this verb like felines or "cat people". Likewise, we could have a subject like "Snow White" determining a sublist of possible objects including "apple", "poison", "magic mirror", etc. Note that these sublists are pre-defined for each theme and **not** created during runtime.

## Credits

This work has been brought to you by [Onyxcorp](https://onyxcorp.com/).

* **Ideation**: [Yuri S Villas Boas](https://t3infosecurity.com/en/), André Fidencio Gonçalves
* **Management**: Yuri S Villas Boas
* **Software development**: André Fidencio Gonçalves
* **Themes design**: Yuri S Villas Boas, André Fidencio Gonçalves, [Erik Braga](https://www.instagram.com/suaterapia.financeira/)

Special thanks to:
* [Edson Cilos](https://www.linkedin.com/in/edson-cilos-032a66162/)
* [Daniel Santos](https://www.linkedin.com/in/daniel-san/)

For more information and to collaborate:
* visit: [formosadefense.com/](https://formosadefense.com/);
* read the article on Toptal's technology block: [toptal.com/cryptocurrency/formosa-crypto-wallet-management](https://www.toptal.com/cryptocurrency/formosa-crypto-wallet-management);
* follow us on Twitter at: [@yurivillasboas](https://twitter.com/yurivillasboas);
* contribute at: [geyser.fund/project/formosa](https://geyser.fund/project/formosa).
