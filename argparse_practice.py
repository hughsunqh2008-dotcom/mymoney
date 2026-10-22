import argparse
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose',
                    help='Increase verbosity.',
                    action='store_true'
                    )
parser.add_argument('square',
                    type=int,
                    help='Return its square.'
                    )
args = parser.parse_args()
print(args,type(args),sep=' ')
answer = args.square**2
if args.verbose:
    print(f"the square of {args.square} equals {answer}")
else:
    print(answer)