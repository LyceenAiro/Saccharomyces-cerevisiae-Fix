# chusan rating
import math


def get_rating(score, level):
    if score >= 1009000:
        rating = level + 2.15
        rank = "SSS+"
    elif score >= 1007500:
        lim = math.floor((score - 1007500) / 100)
        rating = level + 2.0 + 0.01 * lim
        rank = "SSS"
    elif score >= 1005000:
        lim = math.floor((score - 1005000) / 50)
        rating = level + 1.5 + 0.01 * lim
        rank = "SS+"
    elif score >= 1000000:
        lim = math.floor((score - 990000) / 100)
        rating = level + 1 + 0.01 * lim
        rank = "SS"
    elif score >= 975000:
        lim = math.floor((score - 990000) / 250)
        rating = level + 0.01 * lim
        if score >= 990000:
            rank = "S+"
        else:
            rank = "S"
    elif score >= 900000:
        # AA
        lim = round(5 * ((score - 900000) / 100000), 2)
        rating = level - ( 5 - lim )
        if score >= 950000:
            rank = "AAA"
        elif score >= 925000:
            rank = "AA"
        else:
            rank = "A"
    elif score >= 500000:
        # BBB
        lim = round(2 * ((score - 800000) / 100000), 2)
        rating = ( level - 5 ) / ( 2 - lim )
        if score >= 800000:
            rank = "BBB"
        else:
            # BBB-
            lim = round((score - 500000) / 300000, 2)
            rating = round(rating * lim, 2)
            if score >= 700000:
                rank = "BB"
            elif score >= 600000:
                rank = "B"
            else:
                rank = "C"
        rating = rating
    else:
        rating = 0
        rank = "D"

    if rating < 0:
        rating = 0
    
    return round(rating, 2), rank