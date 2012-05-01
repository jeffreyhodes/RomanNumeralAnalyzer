"""
Data type that stores information about a section of a Mozart piano sonata
"""

class Section(object):
  
  def __init__(self, numeral, fdict, bottom, rset):
    self.numeral = numeral
    self.fdict = scale(fdict)
    self.bottom = bottom
    self.rset = rset
 
  """
  Return the similarity score of this Section to the given section
  """
  def distance(self, other):
    reqs = self.rset.union(other.rset)
    start = 0
    for x in reqs:
      if not x in other.fdict:
        start = 200
        break
    return (start + dict_distance(self.fdict, other.fdict) + 
        1 * bottom_distance(self.bottom, other.bottom))

  def __repr__(self):
    return '{0} {1} {2}'.format(self.numeral, self.fdict, self.bottom)

"""
Reads a Section object from a string like
V\n25\n0 0 0 0 0 0 0 0 0 0 0 0 \n0 0 0 0 0 0 0 0 0 0 0 0
where line 1 is numeral, line 2 is count, and lines 3 and 4
are hist and bottom hist, respectively
"""
def from_string(s):
  fields = s.split('\n')
  if not len(fields) == 4:
    return None
  numeral = fields[0]
  
  hist = map(float, fields[1].split())
  bottomhist = map(float, fields[2].split())
  required = map(lambda x: x == '1', fields[3].strip().split())
  
  fdict = dict() 
  for i, x in enumerate(hist):
    if x > 0:
      fdict[i] = x

  bottom = None
  for i, x in enumerate(bottomhist):
    if x > 0:
      bottom = i
      break
  rset = set()
  for i, x in enumerate(required):
    if x:
      rset.add(i)
  
  return Section(numeral, fdict, bottom, rset)

"""
Returns a section that represents the given notes in the given key
"""
def from_notes(notes, k):
  fdict = rotate(dur_dict(notes), k)
  bottom = get_bottom(notes, k)
  rset = set()

  return Section(None, fdict, bottom, rset)

"""
Returns the pitch class of the note with lowest pitch, or None if 
that note is within a third of the next lowest note
"""
def get_bottom(notes, k):
  s_notes = sorted([(n.pitch.midi, n) for n in notes])
  if len(notes) < 1:
    return None
  lowest_midi = s_notes[0][0]
  
  if len(notes) == 1:
    return None

  for p, n in s_notes:
    if not p == lowest_midi:
      if p - lowest_midi > 2 or n.offset == s_notes[0][1].offset:
        return (lowest_midi - k) % 12
      else:
        return None
  return None

"""
Returns a dictionary of total pitch class duration for the given pitch 
list
"""
def dur_dict(notes):
  passing_weight = 0.5
  nonpassing_weight = 3
  result = dict()
  for n in notes:
    p = n.pitch.pitchClass
    d = n.duration.quarterLength
    if not p in result:
      result[p] = 0
    if n.isPassing:
      result[p] += passing_weight * d
    else:
      result[p] += nonpassing_weight * d
  return result

"""""
Returns the given pitch frequency dict transposed from C into the key with pitch
class k
"""
def rotate(fdict, k):
  result = dict()
  for p in fdict:
    result[(p - k) % 12] = fdict[p]
  return result

"""
Scales given frequency dict so that its values sum to 1
"""
def scale(fdict):
  result = dict()
  s = sum((fdict[p] for p in fdict))
  if s == 0:
    s = 1
  for p in fdict:
    result[p] = float(fdict[p]) / s
  return result

def dict_distance(d1, d2):
  result = 0
  for i in d1:
    x1 = d1[i]
    if i in d2:
      x2 = d2[i]
      result += (x1 - x2) * (x1 - x2)
    else:
      result += x1 * x1
  for i in d2:
    x2 = d2[i]
    if not i in d1:
      result += x2 * x2
  return result

def bottom_distance(bot1, bot2):
  if bot1 == None and not bot2 == None:
    return 101
  if bot2 == None and not bot1 == None:
    return 101
  if bot1 == bot2:
    return 0
  return 2
