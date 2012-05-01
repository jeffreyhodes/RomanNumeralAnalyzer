import sys
import os

import pynote
import pychord
import label

"""
generates an analysis from a file, as a list of tuples
(measure, start, stop, key, numeral)
"""
def from_file(filename):
  if not os.path.exists(filename):
    return None
  f = open(filename, 'r')
  k = None
  maj = None
  result = []
  numbeats = 4
  top = 4
  bot = 4
  offset = 0
  for line in f.readlines():

    # Determine number of beats per measure
    if 'ime signature' in line.lower():
      top = int(line[line.index('/') - 1])
      bot = int(line[line.index('/') + 1])
      if bot == 4:
        numbeats = top
      elif (top, bot) == (2, 2):
        numbeats = 4
      elif (top, bot) == (3, 8):
        numbeats = 1.5
      elif (top, bot) == (6, 8):
        numbeats = 3
    
    if 'Measure duration' in line:
      numbeats = float(line.split()[2])

    if line[0] != 'm' or line.find('var') > 0:
      continue
    toks = line.split()
    if toks[0][1:].isdigit():
      m_num = int(toks[0][1:])
    else:
      continue
    
    for i, s in enumerate(toks):
      if s.find(':') > 0:
        key = s[:s.index(':')]
        k = pynote.from_string(key).pitch_class
        maj = key.isupper()
      else:
        if pychord.is_valid_numeral(s):
          j = i - 1
          while j >= 0 and not _is_beat_label(toks[j]):
            j -= 1
          if j < 0:
            beat = 1
          else:
            beat = float(toks[j][1:]) 
          start = get_beat(beat, top, bot)
          stop = start
          result.append((0, m_num, float(start), float(stop), k, maj,
              pychord.numeral_reformatted(s)))
  f.close()
  for i, lab in enumerate(result):
    s, m, start, stop, k, maj, r = lab
    if i + 1 < len(result) and result[i + 1][1] == m:
      result[i] = s, m, start, result[i + 1][2], k, maj, r
    else:
      result[i] = s, m, start, float(numbeats), k, maj, r

  objresult = []
  for s, m, start, stop, key, maj, r in result:
    objresult.append(label.Label(s, m, start, stop, key, maj, r))
  return objresult

"""
Transforms beat from analysis scale to music21 scale
"""
def get_beat(beat, top, bot):
  if bot == 4:
    return beat - 1
  elif (top, bot) == (2, 2):
    return (beat - 1) * 2
  elif (top, bot) == (3, 8):
    return (beat - 1) / 2
  elif (top, bot) == (6, 8):
    return round((beat - 1) * 3) / 2
  else:
    return beat
 
"""
Returns true if token is a lower case b followed by a 
floating-point number
"""
def _is_beat_label(token):
  if len(token) < 2 or not token[0] == 'b':
    return False

  num = token[1:]
  try:
    float(num)
    return True
  except:
    return False
