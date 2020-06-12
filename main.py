from dividend_tracker import *
from push_to_sheets import *


def main():
    download_write_csv()
    calculate_dividend_received()
    push_sheets()


if __name__ == "__main__":
    main()
