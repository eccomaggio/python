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


# pattern = """
# volume number (restart)=11
# year month
# monthly
# refresh(jan 15, aug 15)
# combine(jul , aug)
# """
pattern = """
year month day
daily
omit(Saturday)
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
enumeration = ["volume", "tome", "series", "number", "issue", "fascicle", "fascicule", "sub-parts", "section", "part", "book", "sub-series", "fasc", "part", "vol", "no", "prt", "heft"]
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

days = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday",
  "mon",
  "tue",
  "wed",
  "thu",
  "fri",
  "sat",
  "sun",
  "mo",
  "tu",
  "we",
  "th",
  "fr",
  "sa",
  "su",
  "tues",
  "weds",
  "thur",
  "thurs"
]

months = [
  "jan",
  "feb",
  "mar",
  "apr",
  "may",
  "jun",
  "jul",
  "aug",
  "sep",
  "oct",
  "nov",
  "dec",
  "sept",
  "january",
  "february",
  "march",
  "april",
  "june",
  "july",
  "august",
  "september",
  "october",
  "november",
  "december",
]

seasons = [
  "spring",
  "summer",
  "autumn",
  "winter",
  "fall",
]

ordinals = [
  "first",
  "second",
  "third",
  "fourth",
  "fifth",
  "last",
  "1st",
  "2nd",
  "3rd",
  "4th",
  "5th",
  "6th",
  "7th",
  "8th",
  "9th",
  "10th",
  "11th",
  "12th",
  "13th",
  "14th",
  "15th",
  "16th",
  "17th",
  "18th",
  "19th",
  "20th",
  "21st",
  "22nd",
  "23rd",
  "24th",
  "25th",
  "26th",
  "27th",
  "28th",
  "29th",
  "30th",
  "31st",
]

digits = "1234567890"

chron_patterns = {
    "day": "d",
    "ordinal+literal_day": "d",
    "month+int": "d",
    "ord+day": "w",
    "ord+day+month": "w",
    "ord+literal_week+month": "w",
    "month": "m",
    "season": "s",
    "year+year": "y",
}


def id_parts(raw_line):
  label = ""
  match = re.match(r"[a-z0-9]+", raw_line)
  if match:
    head = match.group()
    # print(f">>>>>{head} in {raw_line}")
    if head in enumeration:
      label = "enumeration"
    elif head in chronology:
      label = "chronology"
    elif head in frequency or head[0] in digits:
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


def identify_param(param:str) -> str:
  param_type = ""
  if param == "day":
    param_type = "literal_day"
  elif param == "week":
    param_type = "literal_week"
  elif param in days:
    param_type = "day"
  elif param in months:
    param_type = "month"
  elif param in seasons:
    param_type = "season"
  elif param in ordinals:
    param_type = "ordinal"
  elif re.match(r'1[6789]\d{2}|20\d{2}',param):
    param_type = "year"
  elif param.isnumeric():
    param_type = "int"
  else:
    param_type = "unknown"
  return param_type


def get_code(_type:str, value:str):
  # if _type in ["day", "month"]:
  #   value = value[:3]
  if _type == "day":
    return value[:2]
  match _type:
    case "day":
      result = f"{days.index(value) + 1}"
    case "month":
      result = f"{months.index(value[:3]) + 1}"
    case "season":
      result = f"{seasons.index(value) + 1}"
    case _:
      result = ""
  if result and len(result) == 1:
    result = f"0{result}"
  return result


def tokenise_regex(raw_line):
    raw_line = re.sub(r'[,/]', "|", raw_line)
    raw_line = raw_line.replace(",", "@|")
    # print(raw_line)
    new = find_params(raw_line)
    return new.split()


def find_params(string):

  def transform_brackets(match):
    prefix = match.group(1)
    content = match.group(3)
    suffix = match.group(5)

    # 1) Change all spaces and commas inside the brackets to "@"
    # transformed_content = re.sub(r" ", "@", content)
    transformed_content = content.replace(" ", "@")
    # 2) Replace first bracket with "@",
    # 3) delete final bracket (omitted in return)
    # 4) Leave prefix and suffix (outside spaces/text) untouched
    return f"{prefix}@{transformed_content}{suffix}"

  # Regex breakdown:
  # Group 1 (.*?\w+) : Captures leading spaces and the final word character before the bracket
  # \s*              : Matches and drops any spaces immediately before the opening bracket
  # Group 2 (\()   : The first opening bracket
  # Group 3 (.*?)  : Content inside the brackets
  # Group 4 (\))   : The final closing bracket
  # Group 5 (.*)   : Any trailing text/spaces outside
  pattern = r"^(.*?\w+)\s*(\()(.*?)(\))(.*)$"

  result = re.sub(pattern, transform_brackets, string)
  # print(f"\t{result}")
  return result


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
  # print(f"!!enum: {pattern}")
  return pattern


def build_chronology(line:Line, pattern:Pattern):
  field_marker = "i" if pattern.enumeration else "a"
  pattern.chronology = []
  # chron = Chronology()
  for i, token in enumerate(line.tokens):
    expanded = token.split("@")
    chron = Chronology()
    chron.caption = expanded[0]
    chron.subfield = chr(ord(field_marker) + i)
    pattern.chronology.append(chron)
  return pattern


def build_frequency(line:Line, pattern:Pattern):
  """
  $w can be followed by:
    a number (similar to $u) or
    an adverb of frequency
  """
  if line.tokens[0][0] in "1234567890":
    match = re.match(r"\d+",line.tokens[0] )
    freq = match.group()
  else:
    freq = frequency_lookup.get(line.tokens[0], "unknown")
  # print(frequency_lookup, line[0], freq)
  pattern.frequency = freq
  return pattern

def build_refresh(line:Line, pattern:Pattern):
  """
  $x can be followed by a series of:
  month: Jan
  month + day : Mar 3
  season: spring
  In DSL, series separated by comma or slash
  """
  value = line.tokens[0]
  param_string = value[value.index("@") : ]
  params = []
  for part in param_string.split("|"):
    params.append([el for el in part.split("@") if el])
  print(f"\t{params=}")
  refreshes = []
  for param in params:
    if len(param) == 1:
      month_or_season = param[0]
      val = get_code("month", month_or_season)
      if not val:
        val = get_code("season", month_or_season)
      val = val if val else "?"
      refreshes.append(val)
    else:
      month, day = param
      month = month[:3]
      month_no = months.index(month) + 1
      month = f"month_no" if month_no > 9 else f"0{month_no}"
      refreshes.append(month + day)
  pattern.refresh = ",".join(refreshes)
  return pattern


def build_exceptions(line:Line, pattern:Pattern) -> Pattern:
  """
  Currently only deals with chronology type
  nb. token = each publication code
  params could be ranges separated by / or ,
  e.g. combine(jul / aug)
  """
  regularities = []
  for token in line.tokens:
    regularity = Regularity()
    cmd, *params = token.split("@")
    regularity.pub_code = cmd[0]
    # hints = [identify_param(param) for param in params]
    hints = []
    for param in params:
      if param == "|":
        break
      hints.append(identify_param(param))
    hint_string = "+".join(hints)
    # print(f"**{hints}->{hint_string} ({params})")
    regularity.chron_code_def = chron_patterns.get(hint_string, "unknown")
    param_string = ""
    for param in params:
      if param == "|":
        param_string += ","
      else:
        param_string += get_code(identify_param(param), param)
    regularity.chron_code = param_string.split(",")
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


def pattern_to_marc(pattern:Pattern) -> str:
  marc = ""
  for enum in pattern.enumeration:
    unit = f"({enum.unit})" if enum.hide else enum.unit
    total_per_cycle = f"$u{enum.total_per_cycle}" if enum.total_per_cycle else ""
    marc += f"${enum.subfield}{unit}{total_per_cycle}"

  for chron in pattern.chronology:
    # caption = f"({chron.caption})" if chron.hide else chron.caption
    caption = f"({chron.caption})"
    marc += f"${chron.subfield}{caption}"

  if (freq := pattern.frequency):
    marc += f"$w{freq}"

  if (refresh := pattern.refresh):
    marc += f"$x{refresh}"

  if len(pattern.exceptions) > 0:
    marc += "$y"
    for r in pattern.exceptions:
      marc += f"{r.pub_code}{r.chron_code_def}{",".join(r.chron_code)}"

  return marc


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
  marc = pattern_to_marc(pattern)
  pprint(pattern)
  print(marc)

parse(pattern)
