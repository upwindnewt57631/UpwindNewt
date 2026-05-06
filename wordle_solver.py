import requests

url = "https://github.com/seanpatlan/wordle-words/raw/refs/heads/main/valid-words.csv"
response = requests.get(url)
VALIDWORDS = response.text.split("\n")
VALIDWORDS = [word.lower() for word in VALIDWORDS]

url = "https://raw.githubusercontent.com/seanpatlan/wordle-words/refs/heads/main/word-bank.csv"
response = requests.get(url)
PASTWORDS = response.text.split("\n")
PASTWORDS = [word.lower() for word in PASTWORDS]

EXTENDED = False

def filter(green,yellow,grey) -> [str]:
    global VALIDWORDS , PASTWORDS
    filtered = []

    for word in PASTWORDS if not EXTENDED else VALIDWORDS:
        if len(word) != 5:
            continue
        if any(word[i] != green[i] and green[i] for i in range(5)):
            continue
        if any(letter in grey for letter in word):
            continue
        failed = False
        for i in range(5):
            for yLetter in yellow[i]:
                if word[i] == yLetter or yLetter not in word:
                    failed = True
                    break
            if failed:
                break
        if failed:
            continue
        filtered.append(word)

    return filtered

def best(words):
    best_score = -1
    best_word = None
    word_str = "".join(words)
    for word in words:
        score = sum(word_str.count(letter) for letter in set(word))
        if score > best_score:
            best_score = score
            best_word = word
    return best_word

green = ["" for i in range(5)]
yellow = [[] for i in range(5)]
grey = []
history = ["slate"]
filterd = filter(green,yellow,grey)
while True:
    print(f"Try this word: {history[-1]}\nChance: {100 / len(filterd):.2f}%\nEnter the output the of this word in the form of [g,y,b] ie apple could be gyybb if a was green p was yellow ect")
    resp = input("> ").lower().strip()
    if len(resp) != 5 or any(letter not in "gyb" for letter in resp):
        print("Try a diffrent input")

    for i in range(5):
        if resp[i] == "g":
            green[i] = history[-1][i]
        if resp[i] == "y":
            yellow[i].append(history[-1][i])
        if resp[i] == "b":
            grey += history[-1][i]
    filterd = filter(green,yellow,grey)
    if len(filterd) == 0:
        EXTENDED = True
        filterd = filter(green,yellow,grey)
    best_word = best(filterd)
    history.append(best_word)