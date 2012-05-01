"""
A class representing a section of a piece of music and its analysis
"""
class Label:
  
  def __init__(self, score, measure, start, stop, key, major, rn, notes=None):
    self.score = score
    self.measure = measure
    self.start = start
    self.stop = stop
    self.key = key
    self.major = major
    self.rn = rn
    self.notes = notes

    self.start_int = int(round(2 * start))
    self.stop_int = int(round(2 * stop))
  
  def __repr__(self):
    return '{0:.3f} {1} {2} {3} {4} {5} {6}'.format(self.score, 
      self.measure, self.start, self.stop, self.key, self.major, self.rn)

  def set_start(self, new_start):
    self.start = new_start
    self.start_int = int(round(2 * new_start))

  def set_stop(self, new_stop):
    self.stop = new_stop
    self.stop_int = int(round(2 * new_stop))
  
def from_string(s):
  fields = s.split()
  if not len(fields) == 7:
    print('Error on ' + str(s))
  sc = float(fields[0])
  m = int(fields[1])
  start = float(fields[2])
  stop = float(fields[3])
  k = int(fields[4])
  maj = fields[5] == 'True'
  rn = fields[6]
  return Label(sc, m, start, stop, k, maj, rn)
