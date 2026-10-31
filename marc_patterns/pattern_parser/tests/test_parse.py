import pytest
from pattern_parser.parse import test_label_digits


@pytest.mark.parametrize("numbers", [
  ["11", "literal:ord:11"],
  ["1st", "literal:ord:1st"],
  ["2nd",  "literal:ord:2nd"],
  ["3rd", "literal:ord:3rd"],
  ["5th", "literal:ord:5th" ],
  ["-2", "literal:ord:-2"],
  ["2026", "literal:year:2026"],
  ["1966", "literal:year:1966"],
  ["1066", "literal:int:1066"],
])

def test_label_digits(numbers):
  assert label_digits(numbers)