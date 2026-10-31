import math


def number_of_files(file_size, file_unit, drive_size_gb):
    file_unit = file_unit.upper()
    conversion = {
        "GB": 1,
        "MB": 1000,
        "KB": 1000000,
        "B": 1000000000,
    }[file_unit]
    capacity = (drive_size_gb * conversion) / file_size

    return math.floor(capacity)


tests = (
    (500, "KB", 1, 2000),
    (50000, "B", 1, 20000),
    (5, "MB", 1, 200),
    (4096, "B", 1.5, 366210),
    (220.5, "KB", 100, 453514),
    (4.5, "MB", 750, 166666),
)

for i, test in enumerate(tests, start=1):
    a, b, c, answer = test
    result = number_of_files(a, b, c)
    isCorrect = result == answer
    print(f"{i}: {a}, {b}, {c} \n\t=> {answer} \n\t= {isCorrect} [{result}]\n")
