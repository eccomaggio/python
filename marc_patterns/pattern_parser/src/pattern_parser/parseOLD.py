import re
from pprint import pprint


pattern = """
volume number (restart)=11
year month
monthly
change(january)
combine(jul / aug)
"""

# all literals have up to 3 parts: literal (type) value
# keywords consist of: keyword [keyword]
special_chars = ",*=/()"
alpha = "abcedfghijklmnopqrstuvwxyz"
digit = "1234567890"


literals = {
"monday": "literal:day:monday",
"tuesday": "literal:day:tuesday",
"wednesday": "literal:day:wednesday",
"thursday": "literal:day:thursday",
"friday": "literal:day:friday",
"saturday": "literal:day:saturday",
"sunday": "literal:day:sunday",
"mon": "literal:day:monday",
"mo": "literal:day:monday",
"tues": "literal:day:tuesday",
"tue": "literal:day:tuesday",
"tu": "literal:day:tuesday",
"weds": "literal:day:wednesday",
"wed": "literal:day:wednesday",
"we": "literal:day:wednesday",
"thurs": "literal:day:thursday",
"thur": "literal:day:thursday",
"thu": "literal:day:thursday",
"th": "literal:day:thursday",
"fri": "literal:day:friday",
"sat": "literal:day:saturday",
"sa": "literal:day:saturday",
"sun": "literal:day:sunday",
"su": "literal:day:sunday",

"january": "literal:month:january",
"february": "literal:month:february",
"march": "literal:month:march",
"april": "april",
"may": "literal:month:may",
"june": "literal:month:june",
"july": "literal:month:july",
"august": "literal:month:august",
"september": "literal:month:september",
"october": "literal:month:october",
"november": "literal:month:november",
"december": "literal:month:december",
"jan": "literal:month:january",
"feb": "literal:month:february",
"mar": "literal:month:march",
"apr": "april",
"may": "literal:month:may",
"jun": "literal:month:june",
"jul": "literal:month:july",
"aug": "literal:month:august",
"sept": "literal:month:september",
"sep": "literal:month:september",
"oct": "literal:month:october",
"nov": "literal:month:november",
"dec": "literal:month:december",

"spring": "literal:season:spring",
"summer": "literal:season:summer",
"autumn": "literal:season:autumn",
"fall": "literal:season:autumn",
"winter": "literal:season:winter",
"continued": "literal:_:continuous",
"published": "literal:keyword:publish",
"omitted": "literal:keyword:omit",
"combined": "literal:keyword:combine",
"volume": "literal:enum:volume",
"number": "literal:enum:number",
"part": "literal:enum:part",
"annual": "literal:_:annual",
"bimonthly": "literal:_:bimonthly",
"semiweekly": "literal:_:semiweekly",
"daily": "literal:_:daily",
"biweekly": "literal:_:biweekly",
"semiannual": "literal:_:semiannual",
"biennial": "literal:_:biennial",
"triennial": "literal:_:triennial",
"triweekly": "literal:_:triweekly",
"trimonthly": "literal:_:trimonthly",
"monthly": "literal:_:monthly",
"quarterly": "literal:_:quarterly",
"semimonthly": "literal:_:semimonthly",
"triyearly": "literal:_:triyearly",
"weekly": "literal:_:weekly",
"irregular": "literal:_:irregular",
"variable": "literal:_:variable",
"undetermined": "literal:_:undetermined",
"continuous": "literal:_:continuous",
"restarts": "literal:_:restarts",
"first": "literal:ord:1",
"second": "literal:ord:2",
"third": "literal:ord:3",
"fourth": "literal:ord:4",
"fifth": "literal:ord:5",
"last": "literal:ord:-1",
"year": "literal:year",
"season": "literal:season",
"month": "literal:month",
"day": "literal:day",
"continue": "literal:_:continuous",
"restart": "literal:_:restarts",
"varies": "literal:_:variable",
"var": "literal:_:variable",
"und": "literal:_:undetermined",

"enumeration": "keyword:enumeration",
"chronology": "keyword:chronology",
"enum": "keyword:enum",
"chron": "keyword:chron",
"frequency": "keyword:frequency",
"change": "keyword:change",
"exception": "keyword:exception",
"combine": "keyword:combine",
"omit": "keyword:omit",
"publish": "keyword:publish",
}


numbers = [
[r"-\d+", "literal:ord:"],
[r"\dth", "literal:ord:"],
[r"\d1st", "literal:ord:"],
[r"\d2nd", "literal:ord:"],
[r"\d3rd", "literal:ord:"],
[r"[12]\d\d\d", "literal:year:"],
[r"\d+", "literal:int:"]
]


# keyword:
# keywords = [
# "enumeration",
# "chronology",
# "enum",
# "chron",
# "frequency",
# "change",
# "exception",
# "combine",
# "omit",
# "publish",
# ]


# def label_literals(chunk, tokens):
#   for literal, expansion in literals:
#       if chunk.startswith(literal):
#         tokens.append(expansion)
#         chunk = chunk[len(literal):]
#   return chunk, tokens

# def label_keywords(chunk, tokens):
#   for keyword in keywords:
#     if chunk.startswith(keyword):
#       tokens.append(f"keyword:{keyword}")
#       chunk = chunk[len(keyword):]
#   return chunk, tokens


def label_digits(chunk):
    for regex, expansion in numbers:
        # if re.prefixmatch(regex, chunk):
        if tmp := re.match(regex, chunk):
            match = tmp[0]
            return f"{expansion}{match}"
    return chunk


# def label_digits(chunk, tokens):
#     for regex, expansion in numbers:
#         # if re.prefixmatch(regex, chunk):
#         if tmp := re.match(regex, chunk):
#             match = tmp[0]
#             tokens.append(f"{expansion}{match}")
#             chunk = chunk[len(match) :]
#     return chunk, tokens


# def label_special_chars(chunk, tokens):
#   # print(f">>>{chunk[0]}_{chunk}_")
#   if chunk[0] in special_chars:
#     tokens.append(chunk[0])
#     chunk = chunk[1:]
#   return chunk, tokens


# def add_labels(raw_line):
#   chunks = raw_line.split()
#   tokens = []
#   for chunk in chunks:
#     while chunk:
#       chunk, tokens = label_special_chars(chunk, tokens)
#       if not chunk:
#         continue
#       chunk, tokens = label_keywords(chunk, tokens)
#       if not chunk:
#         continue
#       chunk, tokens = label_literals(chunk, tokens)
#       if not chunk:
#         continue
#       # tokens.append("#")
#       tokens.append(chunk[0])
#       chunk = chunk[1:]
#   return tokens


def are_same_class(current, previous):
  return (current in alpha and previous in alpha) or (current in digit and previous in digit)


def tokenise(raw_line):
  tokens = []
  token = ""
  for i, char in enumerate(raw_line):
    if i == 0:
      token += char
    else:
      if are_same_class(char, raw_line[i - 1]):
        token += char
      else:
        tokens.append(token)
        token = char
  tokens.append(token)
  tokens = [token for token in tokens if token.strip()]
  return tokens

def expand_tokens(tokens: list[str]):
  expanded = []
  for token in tokens:
    # item = literals.get(token, token)
    item = literals.get(token, "unknown")
    if item == "unknown":
      item = label_digits(token)
    expanded.append(item)
  return expanded


def parse(pattern):
  pattern_lines = [line for line in pattern.splitlines() if line]
  token_lines = []
  # tokens = []
  for i, raw_line in enumerate(pattern_lines):
    tokens = []
    tokens = tokenise(raw_line)
    # tokens = expand_tokens(tokens)
    token_lines.append(tokens)
    # token_lines.append(expand_tokens(tokens))
    # print(f"{i} {tokens}\n\t{raw_line}")
  # pprint(token_lines)
  for line in token_lines:
    print(line)





parse(pattern)
