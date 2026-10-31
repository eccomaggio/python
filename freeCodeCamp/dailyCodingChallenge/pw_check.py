import re


def check_length(pw):
    return len(pw) >= 8


def check_case(pw):
    has_lower = bool(re.search(r"[a-z]", pw))
    has_upper = bool(re.search(r"[A-Z]", pw))
    return has_lower and has_upper


def has_digit(pw):
    return bool(re.search(r"\d", pw))


def has_special_char(pw):
    for char in pw:
        if char in "!@#$%^&*":
            return True
    return False


def check_strength(password):
    print(f"\npassword = {password}")
    score = 0
    checks = [check_length, check_case, has_digit, has_special_char]
    for check in checks:
        score += check(password)
        print(f"{check.__name__} => {check(password)}")
        # if check(password):
        #     score += 1
    if score < 2:
        return "weak"
    elif score == 4:
        return "strong"
    return "medium"


tests = [
    ("123456", "weak"),
    ("pass!!!", "weak"),
    ("Qwerty", "weak"),
    ("PASSWORD", "weak"),
    ("PASSWORD!", "medium"),
    ("PassWord%^!", "medium"),
    ("qwerty12345", "medium"),
    ("S3cur3P@ssw0rd", "strong"),
    ("C0d3&Fun!", "strong"),
]

for i, test in enumerate(tests, start=1):
    a, answer = test
    result = check_strength(a)
    isCorrect = result == answer
    print(
        f"{i}: {a}\n\t=> {result} \n\t= {isCorrect if isCorrect else f'should be: {answer}'}\n"
    )
