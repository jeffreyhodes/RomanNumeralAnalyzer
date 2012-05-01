import sys

import mutils
import mreader
import pychord

"""
Markov Model data type compatible with Mozart analyses
"""
class MarkovModel:
  
  def __init__(self, table, use_inversions):
    self.table = table
    self.use_inversions = use_inversions

  def print_table_pretty(self):
    for s in self.table:
      print(s)
      for t in self.table[s]:
        print(t + ' ' + str(self.table[s][t]))
      print('')

  def print_table(self):
    out = ''
    for s in self.table:
      out = out + s
      for t in self.table[s]:
        out = out + ' ' + t + ' ' + str(self.table[s][t])
      out = out + '\n'
    print(out)


  """
  Returns probability of symbol t following symbol s
  """
  def score(self, s, t):
    if not self.use_inversions:
      s = pychord.just_numeral_with_secondary(s)
      t = pychord.just_numeral_with_secondary(t)
    if s == t:
      return 1
    if not t in self.table[s]:
      return 0
    return self.table[s][t]

  """
  Returns minimum of all transition probabilities in the list
  """
  def listscore(self, xs):
    if not self.use_inversions:
      xs = map(pychord.just_numeral_with_secondary, xs)
    if len(xs) < 2:
      return 1
    scores = [self.score(s, t) for s, t in zip(xs, xs[1:]) if not s == t]
    if len(scores) == 0:
      return 1
    result =  sum(scores) / len(scores)
    return result

def from_analyses(filenames, use_inversions=True):
  ttable = dict()
  for filename in filenames:
    analysis = mreader.from_file(filename)
    if analysis:
      for a, b in zip(analysis, analysis[1:]): 
        k1 = a.key
        rn1 = a.rn
        k2 = b.key
        rn2 = b.rn

        if not use_inversions:
          rn1 = pychord.just_numeral_with_secondary(rn1)
          rn2 = pychord.just_numeral_with_secondary(rn2)
        if k1 == k2:
          if not rn1 in ttable:
            ttable[rn1] = []
          ttable[rn1].append(rn2)
  table = dict()
  for s in ttable:
    temp = dict()
    for t in ttable[s]:
      if not t in temp:
        temp[t] = 0
      temp[t] += 1
    total = sum([temp[t] for t in temp])
    table[s] = dict()
    for t in ttable[s]:
      table[s][t] = float(temp[t]) / total
  return MarkovModel(table, use_inversions)

"""
Loads a markov model stored in a file
"""
def from_file(filename, use_inversions=True):
  f = open(filename, 'r')
  d = dict()
  for line in f.readlines():
    fields = line.split()
    if len(fields) > 0:
      s = fields[0]
      d[s] = dict()
      fields = fields[1:]
      for i in range(0, len(fields), 2):
        d[s][fields[i]] = float(fields[i + 1])
  return MarkovModel(d, use_inversions)

def main():
  model = from_analyses(sys.argv[1:], use_inversions=True)
  model.print_table()

if __name__ == '__main__':
  main()
