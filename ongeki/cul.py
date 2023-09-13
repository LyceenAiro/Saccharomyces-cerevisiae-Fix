import math


def rating(score, level):
    if score >= 1007500:
        rating = level + 2
        rank = "SSS+"
    elif score >= 1000000:
        lim = math.floor((score - 1000000) / 150)
        rating = level + 1.5 + 0.01 * lim
        rank = "SSS"
    elif score >= 990000:
        lim = math.floor((score - 990000) / 200)
        rating = level + 1 + 0.01 * lim
        rank = "SS"
    elif score >= 970000:
        lim = math.floor((score - 970000) / 200)
        rating = level + 0.01 * lim
        rank = "S"
    elif score >= 900000:
        # AA
        lim = round(4 * ((score - 900000) / 70000), 2)
        rating = level - lim
        if score >= 940000:
            rank = "AAA"
        else:
            rank = "AA"
    elif score >= 800000:
        # BBB
        lim = round(2 * ((score - 800000) / 100000), 2)
        rating = level - 4 - lim
        if score >= 850000:
            rank = "A"
        else:
            rank = "BBB"
    else:
        # BBB-
        lim = round((score - 500000) / 300000, 2)
        rating = round((level - 6) * lim, 2)
        if score >= 750000:
            rank = "BB"
        elif score >= 700000:
            rank = "B"
        elif score >= 500000:
            rank = "C"
        else:
            rank = "D"

    if rating < 0:
        rating = 0
    
    return round(rating, 2), rank