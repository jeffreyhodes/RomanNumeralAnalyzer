import os

import hmm

def hmm_from_filenames(filenames):
  data = []
  for name in filenames:
    data.append([])
    f = open(name)
    for line in f.readlines():
      if line[0] == '.':
        data.append([])
      else:
        fields = line.strip().split()
        data[-1].append((fields[0], fields[1]))
  data = [run for run in data if len(run) > 0]
  return hmm.HMM(data)

def hmm_from_training_dir():
  path = 'keytrainingdata/'
  filenames = map(lambda x: path + x, os.listdir(path))
  return hmm_from_filenames(filenames)

def extract_pair(state):
  pair = state.split('-')
  return int(pair[0]), (pair[1] == 'True')

def main():
  model = hmm_from_training_dir()
  print(model.log_start_probs)

if __name__ == '__main__':
  main()
