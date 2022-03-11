import os
import sys
from libs.BitKub import BitKub

# initialize environ
bitkub = BitKub()

def main():
    print(bitkub.API_HOST)


if __name__ == '__main__':
    main()
    sys.exit(0)
