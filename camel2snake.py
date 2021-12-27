import re

strings = [
    "HelloWorld",
    "ILikeApples",
    "HelloImBobAndIm30",
    "300DogsAnd300Cats"
    ]
toFind1 = re.compile(r"([a-z](?=[A-Z0-9]))|([A-Z]|[0-9])(?=[A-Z])")
toFind2 = re.compile(r"(?:[A-Z][a-z]*)|(?:[0-9]+)")
for string in strings:
    out1 = re.sub(toFind1,r'\1\2 ',string)
    out2 = re.findall(toFind2, string)
    out1 = "_".join(out1.split()).lower()
    out2 = "_".join(out2).lower()
    print(out1)
    print(out2)
