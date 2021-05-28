import argparse
import random


def generate_good(goods, ctv):
    print("GOODS:")
    for g in goods:
        print("Id: " + str(g))
        print("CTV: " + str(ctv))
        print("PPV: " + str(random.randint(ctv, 20)))


def generate_neutral(neutrals, ctv):
    print("NEUTRALS:")
    for n in neutrals:
        print("Id: " + str(n))
        print("CTV: " + str(ctv))
        print("PPV: " + str(random.randint(max(ctv - 7, 1), ctv + 7)))


def generate_bad(bads, ctv):
    print("BADS:")
    for b in bads:
        print("Id: " + str(b))
        print("CTV: " + str(ctv))
        print("PPV: " + str(random.randint(1, ctv + 7)))


def main():
    parser = argparse.ArgumentParser(description='Configure the number and the kind of data flows in the test run.')
    parser.add_argument('good', metavar='GOOD', type=int,
                        help='an integer that tells the program how many flows to create with good behaviour')
    parser.add_argument('neutral', metavar='NEUTRAL', type=int,
                        help='an integer that tells the program how many flows to create with neutral behaviour')
    parser.add_argument('bad', metavar='BAD', type=int,
                        help='an integer that tells the program how many flows to create with bad behaviour')

    args = parser.parse_args()

    flows = {}
    flows['good'] = list(range(1, args.good + 1))
    flows['neutral'] = list(range(args.good + 1, args.neutral + args.good + 1))
    flows['bad'] = list(range(args.neutral + args.good + 1, args.bad + args.neutral + args.good + 1))

    print("ARGS:")
    print(args)
    print("FLOWS:")
    print(flows)

    for i in range(20):
        print("ROUND " + str(i))
        ctv = random.randint(5, 15)
        generate_good(flows['good'], ctv)
        generate_neutral(flows['neutral'], ctv)
        generate_bad(flows['bad'], ctv)




if __name__ == '__main__':
    main()