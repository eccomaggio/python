import re
from pprint import pprint
from dataclasses import dataclass, field

"""
enum = $a-$h, $u
chron = $i-$m
frequency = $w (or combined with chron using *)
refresh = $x
combine, publish, omit = $y
[not yet considered = $z]
"""


pattern = """
volume number (restart)=11
year month
monthly
refresh(january)
combine(jul / aug)
"""

# all literals have up to 3 parts: literal (type) value
# keywords consist of: keyword [keyword]
special_chars = ",*=/()"
alpha = "abcedfghijklmnopqrstuvwxyz"
digit = "1234567890"


@dataclass
class Line:
  label:str = ""
  tokens:list[str] = field(default_factory=list)
  dsl:str = ""


@dataclass
class NumberScheme:
  type_of_designation: str = ""
  case: str = ""
  script: str = ""

@dataclass
class Enumeration:
  # scheme: NumberScheme
  subfield: str = ""
  unit: str = ""      # v., no., prt.
  numbering: str = ""  # restart, continuous
  total_per_cycle: int = 0
  hide: bool = False

@dataclass
class Chronology:
  subfield: str = ""
  caption: str = ""         # day, month, year, season
  hide: bool = False

@dataclass
class Regularity:
  pub_code: str = ""          # combined, omitted, published
  chron_code_def: str = ""    # day, month, season, week, year
  chron_code: list[str] = field(default_factory=list)

@dataclass
class Dsl:
  enumeration:str = ""
  chronology:str = ""
  frequency:str = ""
  refresh:str = ""
  exceptions:str = ""

@dataclass
class Pattern:
  enumeration: list[Enumeration] = field(default_factory=list)
  chronology: list[Chronology] = field(default_factory=list)
  frequency: str = ""
  refresh: str = ""
  exceptions: list[Regularity] = field(default_factory=list)
  dsl:Dsl = field(default_factory=Dsl)



chronology = ["year", "month", "season", "week", "day"]
enumeration = ["volume", "tome", "series", "number", "issue", "fascicle", "fascicule", "sub-parts", "section", "part", "book", "sub-series", "fasc", "part", "vol", "no", "prt"]
frequency = [
"annual",
"bimonthly",
"semiweekly",
"daily",
"biweekly",
"semiannual",
"biennial",
"triennial",
"triweekly",
"trimonthly",
"continuously",
"monthly",
"quarterly",
"semimonthly",
"triyearly",
"weekly",
"irregular",
]
exceptions = ["combine", "publish", "omit"]

frequency_lookup = {
"annual" : "a",
"bimonthly" : "b",
"semiweekly" : "c",
"daily" : "d",
"biweekly" : "e",
"semiannual" : "f",
"biennial" : "g",
"triennial" : "h",
"trimonthly" : "j",
"continuously" : "k",
"monthly" : "m",
"quarterly" : "q",
"semimonthly" : "s",
"triyearly" : "t",
"weekly" : "w",
"irregular" : "x",
}


def id_parts(raw_line):
  label = ""
  match = re.match(r"[a-z]+", raw_line)
  if match:
    head = match.group()
    # print(f">>>>>{head} in {raw_line}")
    if head in enumeration:
      label = "enumeration"
    elif head in chronology:
      label = "chronology"
    elif head in frequency:
      label = "frequency"
    elif head in exceptions:
      label = "exception"
    elif head == "refresh":
      label = "refresh"
    # else:
    #   label = "_unknown"
  else:
    label = "unknown"
  return [label, raw_line]


def tokenise_regex(raw_line):
    # new = re.sub(r"\s*\(", "@", raw_line)
    # new = re.sub(r"\)*(\=\d+)", r"@\1", new)
    # new = re.sub(r"(\=\d+)", r"@\1", new)
    new = raw_line.replace("(", "@")
    new = new.replace("/", "@")
    new = new.replace(")","")
    new = new.replace(" ","")
    # new = re.sub(r"(?<=\w)\s*/\s*", "@", new)
    # return [label, *new.split()]
    return new.split()


def build_enumeration(line:Line, pattern:Pattern):
  # pattern.enumeration = []
  for i, token in enumerate(line.tokens):
    expanded = token.split("@")
    enum = Enumeration()
    enum.unit = f"{expanded[0][0]}."
    enum.subfield = chr(97 + i)
    if len(expanded) > 1:
      for el in expanded[1:]:
        if el.startswith("="):
          enum.total_per_cycle = int(el[1:])
        elif el == "hide":
          enum.hide == True
        else:
          enum.numbering = el
    pattern.enumeration.append(enum)
  print(f"!!enum: {pattern}")
  return pattern

def build_chronology(line:Line, pattern:Pattern):
  pattern.chronology = []
  # chron = Chronology()
  for i, token in enumerate(line.tokens):
    expanded = token.split("@")
    chron = Chronology()
    chron.caption = expanded[0]
    chron.subfield = chr(ord("i") + i)
    pattern.chronology.append(chron)
  return pattern

def build_frequency(line:Line, pattern:Pattern):
  freq = frequency_lookup[line.tokens[0]]
  # print(frequency_lookup, line[0], freq)
  pattern.frequency = freq
  return pattern

def build_refresh(line:Line, pattern:Pattern):
  pattern.refresh = f"$x?"
  return pattern

def build_exceptions(line:Line, pattern:Pattern):
  regularities = []
  for token in line.tokens:
    regularity = Regularity()
    cmd, *params = token.split("@")
    regularity.pub_code = cmd[0]
    regularity.chron_code_def = "??"
    regularity.chron_code = params
    regularities.append(regularity)
  pattern.exceptions = regularities
  return pattern

def build_pattern(lines:list[Line]) -> Pattern:
  pattern = Pattern()
  for line in lines:
    match line.label:
      case "enumeration":
        pattern = build_enumeration(line, pattern)
        pattern.dsl.enumeration = line.dsl
      case "chronology":
        pattern = build_chronology(line, pattern)
        pattern.dsl.chronology = line.dsl
      case "frequency":
        pattern = build_frequency(line, pattern)
        pattern.dsl.frequency = line.dsl
      case "refresh":
        pattern = build_refresh(line, pattern)
        pattern.dsl.refresh = line.dsl
      case "exception":
        pattern = build_exceptions(line, pattern)
        pattern.dsl.exceptions = line.dsl
  return pattern


def parse(dsl_string):
  pattern_lines = [line.strip().lower() for line in dsl_string.splitlines() if line]
  lines = []
  for i, raw_line in enumerate(pattern_lines):
    label, dsl = id_parts(raw_line)
    tokens = tokenise_regex(dsl)
    line = Line(label, tokens, dsl)
    lines.append(line)
  # pprint(lines)
  pattern = build_pattern(lines)
  pprint(pattern)

parse(pattern)
