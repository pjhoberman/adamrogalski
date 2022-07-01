import argparse

from illinois import run_illinois
from michigan import run_michigan
from pdfgen import draw

states = ['illinois', 'michigan']


def illinois():
    run_illinois()
    draw(data_file="illinois_data.csv", output_file="illinois.pdf", state="Illinois")


def michigan():
    run_michigan()
    draw(data_file="michigan.csv", output_file="michigan.pdf", state="Michigan")


def main(state):
    state_actions = {
        "illinois": illinois,
        "michigan": michigan,
    }

    if state in state_actions:
        state_actions[state]()
    else:
        print(f"{state} is not coded.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", type=str, required=True, choices=states)

    args = parser.parse_args()
    state = args.state

    main(state)
