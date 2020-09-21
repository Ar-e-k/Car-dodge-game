from pickle import dump

def pic(file, values):
    f=open(file, "wb")
    dump(values, f)
    f.close()

pic("High_scores.high", [0, 0, 0, 0, 0])
