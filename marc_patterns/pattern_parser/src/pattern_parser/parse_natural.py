import re
from pprint import pprint
from dataclasses import dataclass, field
from enum import Enum

"""
enum = $a-$h, $u
chron = $i-$m
frequency = $w (or combined with chron using *)
refresh = $x
combine, publish, omit = $y
[not yet considered = $z]


ISSUES:
frequency: not sure how to represent $w4 in natural language! Currently, it just accepts a number with no attempt to make it sound natural. Phrases are fine.


Maybe:
1) publish 11 numbers with volume number ... (=> $bno.$u11)
2) publish 11 times on year, month ... (=> $w11)
"""


# pattern = """
# volume number (restart)=11
# year month
# monthly
# refresh(jan 15, aug 15)
# combine(jul , aug)
# """
# pattern = """
# year month day
# daily
# omit(Saturday)
# """
pattern = "PUBLISH 11 numbers WITH volume, hidden number (restart) ON year, month EVERY month STARTING jan 15, aug 15 BUT combine july & august"

# pattern = "publish on year, month, day every day but omit saturday"

# all literals have up to 3 parts: literal (type) value
# keywords consist of: keyword [keyword]
special_chars = ",*=/()"
alpha = "abcedfghijklmnopqrstuvwxyz"
digit = "1234567890"


@dataclass
class Line:
  label:str = ""
  # tokens:list[str] = field(default_factory=list)
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


class Cues(Enum):
  enum = " with "
  chron = " on "
  freq = " every "
  refresh = " starting "
  ex = " but "

chronology = ["year", "month", "season", "week", "day"]

# enumeration = ["volume", "tome", "series", "number", "issue", "fascicle", "fascicule", "sub-parts", "section", "part", "book", "sub-series", "fasc", "part", "vol", "no", "prt", "heft"]

enumeration = {
  "volume": "v.",
  "vol": "v.",
  "tome": "t.",
  "series": "ser.",
  "number": "no.",
  "issue": "iss.",
  "fascicle": "fasc.",
  "fascicule": "fasc.",
  "sub-parts": "s-prt.",
  "section": "sec.",
  "part": "prt",
  "book": "bk.",
  "sub-series": "s-ser.",
  "no": "no.",
  "heft": "Heft"}

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

period_designator = {
"year" : "a",
"halfmonth" : "b",
"otherweek" : "c",
"day" : "d",
"halfweek" : "e",
"halfyear" : "f",
"6months" : "f",
"2years" : "g",
"3years" : "h",
"3xweek" : "i",
"3xmonth" : "j",
"month" : "m",
"quarter" : "q",
"3months" : "q",
"othermonth" : "s",
"3xyear" : "t",
"4months" : "t",
"week" : "w",
"sooften" : "x",
}

reverse_cycles = {
"a": "year",
"b": "half month",
"c": "other week",
"d": "day",
"e": "half week",
"f": "half year",
# "f": "6 months",
"g": "2 years",
"h": "3 years",
"i": "3 times a week",
"j": "3 times a month",
"m": "month",
"q": "quarter",
# "q": "3 months",
"s": "other month",
"t": "3 times a year",
# "t": "4 months",
"w": "week",
"x": "so often",
}



chron_patterns = {
    "day": "d",
    "ordinal+literal_day": "d",
    "month+int": "d",
    "ord+day": "w",
    "ord+day+month": "w",
    "ord+literal_week+month": "w",
    "month": "m",
    "month+month": "m",
    "season": "s",
    "year+year": "y",
}


def get_cycle(string):
  cycle = string.replace("times", "x").replace("a", "")
  return cycle.replace(" ", "")


def tail_n_head(string, separator=","):
  # guaranteed to return a tuple of two parts
  # if only one part, then the first part is empty
  if string:
    head_tail = string.split(separator, 1)
    if len(head_tail) == 1:
      return ["", head_tail[0]]
    else:
      return head_tail
  else:
    return ["",""]


def tidy(string:str) -> str:
  s = string.replace(", ", " ")
  s = s.replace(",", " ")
  return s.strip()


def divide_into_series(string:str) -> list[str]:
  return [el.strip() for el in string.split(",") if el.strip()]


# def resolve_sections(raw_line:str) -> list[list[str]]:
def resolve_sections(raw_line:str) -> list[Line]:
  lines = []
  total, enumeration, chronology, frequency, refresh, exceptions = ["", "", "", "", "", ""]

  raw_line = raw_line.lower()
  raw_line = re.sub(r'\s+', " ", raw_line)  # flatten spaces to single
  raw_line = raw_line.replace(" &", ",")
  raw_line = raw_line.replace(" and ", ", ")
  raw_line = re.sub(r'[/|&]', ",", raw_line) # allow only comma as separator
  if raw_line.startswith("publish"):
    raw_line = raw_line[7:]

  total, rest = tail_n_head(raw_line, Cues.enum.value)
  enumeration, rest = tail_n_head(rest, Cues.chron.value)
  chronology, rest = tail_n_head(rest, Cues.freq.value)
  frequency, rest = tail_n_head(rest, Cues.refresh.value)
  refresh, exceptions = tail_n_head(rest, Cues.ex.value)

  total_norm = [el.strip() for el in total.split(" ") if el.strip()]
  if len(total_norm) == 1:
    total_norm.append("")
  enumeration_norm = tidy(enumeration.replace("hidden ", "-"))
  enumeration_norm = enumeration_norm.replace(" (", "@").replace(")", "")
  chronology_norm = tidy(chronology.replace("explicit ", "+"))
  frequency_norm = re.sub(r'^(\d+)$', "_\1", frequency).strip()
  refresh_norm = divide_into_series(refresh)
  exceptions_norm = [exceptions]

  lines = [
    Line("total", total_norm, f"publish {total}"),
    Line("enumeration", enumeration_norm.split(), enumeration),
    Line("chronology", chronology_norm.split(), chronology),
    Line("frequency", [frequency_norm], frequency),
    Line("refresh", refresh_norm, refresh),
    Line("exceptions", exceptions_norm, exceptions),
  ]
  return lines


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


def build_enumeration(line:Line, pattern:Pattern, total:str, restricted_to:str):
  for i, token in enumerate(line.tokens):
    tmp = token.split("@")
    if len(tmp) == 1:
      unit, numbering = tmp[0], ""
    else:
      unit, numbering = tmp
    hidden = False
    if unit.startswith("-"):
      hidden = True
      unit = unit[1:]

    enum = Enumeration()
    enum.numbering = numbering
    enum.unit = f"{unit[0]}."
    enum.subfield = chr(97 + i)
    if enum.unit[0] == restricted_to[0]:
      enum.total_per_cycle = int(total)
    enum.hide = hidden
    pattern.enumeration.append(enum)
  # print(f"!!enum: {pattern}")
  return pattern


def build_chronology(line:Line, pattern:Pattern):
  field_marker = "i" if pattern.enumeration else "a"
  pattern.chronology = []
  for i, token in enumerate(line.tokens):
    hidden = True
    if token.startswith("+"):
      hidden = False
      token = token[1:]
    chron = Chronology(
      chr(ord(field_marker) + i),
      token,
      hidden,
    )
    pattern.chronology.append(chron)
  return pattern


def build_frequency(line:Line, pattern:Pattern):
  """
  DSL could be
  $w can be followed by:
    a number (similar to $u) or
    an adverb of frequency
    if a number, it will be prefixed by underscore
  """
  frequency_text = line.tokens[0]
  if frequency_text.startswith("_"):
    freq = line.tokens[0][1:]
  else:
    freq = period_designator.get(frequency_text, "unknown")
  pattern.frequency = freq
  return pattern


def build_refresh(line:Line, pattern:Pattern):
  """
  $x can be followed by a series of:
  month: Jan
  month + day : Mar 3
  season: spring
  In DSL, series separated by comma
  so:
    [series1, series2] or [[param1a, param1b], [param2a, param2b]]
  """
  refreshes = []
  for series in line.tokens:
    params = series.split(" ")
    if len(params) == 1:
      month_or_season = params[0]
      val = get_code("month", month_or_season)
      if not val:
        val = get_code("season", month_or_season)
      val = val if val else "?"
      refreshes.append(val)
    elif len(params) == 2:
      month, day = params
      month = month[:3]
      month_no = months.index(month) + 1
      month = f"{month_no}" if month_no > 9 else f"0{month_no}"
      refreshes.append(month + day)
  pattern.refresh = ",".join(refreshes)
  return pattern


def identify_exception_series(token:list[str]) -> list[Regularity]:
  ## each series starts with publication code
  series:list[Regularity] = []
  value = token[0].replace(",", "")
  i = -1
  for el in value.split(" "):
    if el in ["combine", "omit", "publish"]:
      series.append(Regularity(el[0], "", []))
      i += 1
    else:
      series[i].chron_code.append(el)
  return series


def identify_exception_pattern_type(exception:Regularity) -> Regularity:
  hints = []
  for param in exception.chron_code:
    hints.append(identify_param(param))
  hint_string = "+".join(hints)
  for i, hint in enumerate(hints):
    exception.chron_code[i] = get_code(hint, exception.chron_code[i])
  exception.chron_code_def = chron_patterns.get(hint_string, "unknown")
  return exception


def build_exceptions(line:Line, pattern:Pattern) -> Pattern:
  """
  Currently only deals with chronology type
  nb. token = each publication code
  params could be ranges separated by ,
  e.g. combine(jul , aug)
  """
  series = identify_exception_series(line.tokens)
  for exception in series:
    exception = identify_exception_pattern_type(exception)
  pattern.exceptions = series
  return pattern


def build_pattern(lines:list[Line]) -> Pattern:
  pattern = Pattern()
  total, restricted_to = "", ""
  for line in lines:
    match line.label:
      case "total":
        total, restricted_to = line.tokens
      case "enumeration":
        pattern = build_enumeration(line, pattern, total, restricted_to)
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
      case "exceptions":
        pattern = build_exceptions(line, pattern)
        pattern.dsl.exceptions = line.dsl
      case _:
        return pattern
  return pattern


def pattern_to_marc(pattern:Pattern) -> str:
  marc = ""
  for enum in pattern.enumeration:
    unit = f"({enum.unit})" if enum.hide else enum.unit
    total_per_cycle = f"$u{enum.total_per_cycle}" if enum.total_per_cycle else ""
    numbering = f"$v{enum.numbering[0]}" if enum.numbering else ""
    marc += f"${enum.subfield}{unit}{total_per_cycle}{numbering}"

  for chron in pattern.chronology:
    caption = f"({chron.caption})" if chron.hide else chron.caption
    marc += f"${chron.subfield}{caption}"

  if (freq := pattern.frequency):
    marc += f"$w{freq}"

  if (refresh := pattern.refresh):
    marc += f"$x{refresh}"

  if len(pattern.exceptions) > 0:
    marc += "$y"
    predicate = []
    for r in pattern.exceptions:
      separator = "/" if r.pub_code == "c" else ""
      # marc += f"{r.pub_code}{r.chron_code_def}{separator.join(r.chron_code)}"
      predicate.append(f"{r.pub_code}{r.chron_code_def}{separator.join(r.chron_code)}")
    marc += ",".join(predicate)
  return marc


def parse(dsl_string:str):
  print(f"\norig >> {dsl_string}")
  lines = resolve_sections(dsl_string)
  pattern = build_pattern(lines)
  marc = pattern_to_marc(pattern)
  # pprint(lines)
  # pprint(pattern)
  print(marc)
parse(pattern)
