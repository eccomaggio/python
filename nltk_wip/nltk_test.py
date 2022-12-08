import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')


synonyms = []
antonyms = []

for synset in wordnet.synsets("evil"):
    for l in synset.lemmas():
        synonyms.append(l.name())
        if l.antonyms():
            antonyms.append(l.antonyms()[0].name())
print(set(synonyms))
print(set(antonyms))
