import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--files', type=str, nargs='+')
parser.add_argument('--output-file', dest='outputFile', type=str, required=True)
parser.add_argument('--task', type=int, choices=[1, 2], required=True)

args = parser.parse_args()

results = []
for filename in args.files:
  df = pd.read_csv(filename, sep='\t', header=0)
  filename = filename.split('/')[-1].split('.')[0]
  print("Filename: ", filename)
  if args.task == 1:
    meanNDCG = df["nDCG"].mean()
    meanAWRF = df["AWRF"].mean()
    meanScore = df["Score"].mean()

    print("Mean nDCG: ", meanNDCG)
    print("Mean AWRF: ", meanAWRF)
    print("Mean Score: ", meanScore)
    print()
    results.append([filename, meanNDCG, meanAWRF, meanScore])
  elif args.task == 2:
    meanEEL = df["EE-L"].mean()
    meanEER = df["EE-R"].mean()
    meanEED = df["EE-D"].mean()

    print("Mean EE-L: ", meanEEL)
    print("Mean EE-R: ", meanEER)
    print("Mean EE-D: ", meanEED)
    print()
    results.append([filename, meanEEL, meanEER, meanEED])

if args.task == 1:
  results = pd.DataFrame(results, columns=['run', 'Mean nDCG', 'Mean AWRF', 'Mean Score'])
elif args.task == 2:
  results = pd.DataFrame(results, columns=['run', 'Mean EE-L', 'Mean EE-R', 'Mean EE-D'])

results.to_csv(args.outputFile, sep='\t', float_format='%.3f')
