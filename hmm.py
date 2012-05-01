from math import log

"""
Hidden Markov Model class.  Builds itself from a set of training data
and contains an implementation of the Viterbi algorithm
"""
class HMM:

  dummy_output = '' 

  """
  data is a list of lists of pairs of strings (state, obs)  
  """
  def __init__(self, data):
    self.states = set()
    self.outputs = set()
    for run in data:
      for state, output in run:
        self.states.add(state)
        self.outputs.add(output)
    
    # add dummy output for never-seen ones
    self.outputs.add(HMM.dummy_output)
   
    # set up counting structures 
    starts_per_state = dict()
    for state in self.states:
      starts_per_state[state] = 1

    outputs_per_state = dict()
    for state in self.states:
      outputs_per_state[state] = dict()
      for output in self.outputs:
        outputs_per_state[state][output] = 1

    states_per_state = dict()
    for state in self.states:
      states_per_state[state] = dict()
      for state2 in self.states:
        states_per_state[state][state2] = 1

    # run through data  
    for run in data:
      N = len(run)
      start_state, _ = run[0]
      starts_per_state[start_state] += 1
      for i, (state, output) in enumerate(run):
        outputs_per_state[state][output] += 1
        if i < N - 1:
          next_state, _ = run[i + 1]
          states_per_state[state][next_state] += 1
    
    self.log_start_probs = self._compute_log_probs(starts_per_state)
    self.log_output_probs = dict()
    for state in self.states:
      self.log_output_probs[state] = self._compute_log_probs(
          outputs_per_state[state])
    self.log_transition_probs = dict()
    for state in self.states:
      self.log_transition_probs[state] = self._compute_log_probs(
          states_per_state[state])

  """
  Uses the Viterbi algorithm to compute the most likely sequence of states
  corresponding to the given sequence of outputs
  """
  def most_likely_sequence(self, outputs):
    N = len(outputs)
    for i in range(N):
      if not outputs[i] in self.outputs:
        outputs[i] = HMM.dummy_output

    v = [dict() for i in range(N)]
    prev = [dict() for i in range(N)]
    for state in self.states:
      v[0][state] = (self.log_start_probs[state] + 
          self.log_output_probs[state][outputs[0]])
      prev[0][state] = -1

    for i in range(1, N):
      for x in self.states:
        max = None
        max_state = None
        for y in self.states:
          p = (v[i - 1][y] + self.log_transition_probs[y][x] + 
              self.log_output_probs[x][outputs[i]])
          if max == None or p > max:
            max = p
            max_state = y
        v[i][x] = max
        prev[i][x] = max_state
    
    max = None
    max_state = None
    for x in self.states:
      if max == None or v[N - 1][x] > max:
        max = v[N - 1][x]
        max_state = x
    
    result = [None for i in range(N)]
    for i in range(N - 1, -1, -1):
      result[i] = max_state
      max_state = prev[i][max_state]

    return result
    
  def _compute_log_probs(self, d):
    total = sum(d[k] for k in d)
    result = dict()
    for k in d:
      result[k] = log(float(d[k]) / total)
    return result

def main():
  data = []
  data.append([])
  f = open('mtrain/01-1-00.txt')
  for line in f.readlines():
    if line[0] == '.':
      data.append([])
    else:
      fields = line.strip().split()
      data[-1].append((fields[0], fields[1]))
  data = [run for run in data if len(run) > 0]
  testdata = [output for state, output in data[0]]
  
  model = HMM(data) 
  print(model.most_likely_sequence(testdata))

if __name__ == '__main__':
  main()
