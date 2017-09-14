for i in range(1, 101):
    if "7" in str(i) and i % 7 == 0:
        print("hackita!")
    elif "7" in str(i):
        print("bang!")
    elif i % 7 == 0:
        print("boom!")
    else:
        print(i)

