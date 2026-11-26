import sys
from src.parse import parse_map


def main() -> None:
    filename = sys.argv[1]
    try:
        sim_map = parse_map(filename)
        print(sim_map)
    except Exception as error:
        print(error)
    print("Hello world!")


if __name__ == "__main__":
    main()
