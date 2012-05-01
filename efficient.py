from music21 import stream, note, chord, converter, meter

import mutils

pickups = [
  'mozart/xml/01-2.xml',
  'mozart/xml/01-3.xml',
  'mozart/xml/02-3.xml',
  'mozart/xml/03-3.xml',
  'mozart/xml/05-1.xml'
]


"""
Some movements have repeats inside of measures.  music21 counts this as
two measures, making everything off by one after the repeat. This lists
the movements and the offending measure.
"""
repeats = [
  ('mozart/xml/01-2.xml', 28),
  ('mozart/xml/01-3.xml', 56),
  ('mozart/xml/02-3.xml', 80),
  ('mozart/xml/04-3.xml', 40),
  ('mozart/xml/05-1.xml', 53)
]

class EfficientScore:
  
  def __init__(self, filename):
      
    self.filename = filename
    self.d = dict()
    self.time_sig = None
    self.measure_nums = []

    self.s = converter.parse(filename)

    self._mark_passing_tones()

    if filename.endswith('xml'):
      self._set_dict_from_xml(self.s)
    elif filename.endswith('krn'):
      self._set_dict_from_krn(self.s)
    else:
      raise Error()
    
    self.measure_nums = sorted(list(set(self.measure_nums)))

  def show_measure(self, n):
    if n < 1: 
      return 
    for m in self.d[n]:
      m.flat.show('text')

  def notes_in_measure(self, n, start, stop):
    result = []
    if n < 1: 
      return []
    for m in self.d[n]:
      notes_and_chords = m.flat.getElementsByOffset(start, stop,
            includeEndBoundary=False, mustBeginInSpan=False)
      for nc in notes_and_chords:
        if isinstance(nc, note.Note):
          result.append(nc)
        elif isinstance(nc, chord.Chord):
          for pit in nc.pitches:
            n = note.Note(pit)
            n.duration = nc.duration
            n.isPassing = nc.isPassing
            n.offset = nc.offset
            result.append(n)
    return result   

  def _notes_in_object(self, o):
    result = []
    if isinstance(o, note.Note):
      result.append(o)
    elif isinstance(o, chord.Chord):
      for pit in o.pitches:
        n = note.Note(pit)
        n.duration = o.duration
        n.isPassing = c.isPassing
        n.offset = nc.offset
        result.append(n)


  """
  Returns a list of all notes in this score
  """
  def all_notes(self):
    return self.s.flat.notes
  
  """
  Returns a list of outputs from this score for use by hmm in the
  Viterbi algorithm
  """
  def output_list(self):
    ts = self.time_sig
    L = mutils.num_eighths_in_measure(ts.numerator, ts.denominator)
    result = []
    for m in self.measure_nums:
      for i in range(L):
        start = float(i) / 2
        stop = float(i + 1) / 2
        notes = self.notes_in_measure(m, start, stop)
        result.append(self._as_observation(notes))
    return result

  def output_string_list(self):
    outputs = self.output_list()
    return map(self._as_string, outputs)
  
  def _as_observation(self, notes):
    s_notes = sorted([(n.pitch.midi, n) for n in notes])
    if len(notes) == 0:
      return None
    bot = s_notes[0][1].pitch.pitchClass
    ps = set([n.pitch.pitchClass for n in notes])
    return (ps, bot)

  def _as_string(self, obs):
    if obs:
      ps, b = obs
      return ','.join(map(str, sorted(list(ps))))
    else:
      return 'None'

  """
  Stores a boolean property n.isPassing on each note
  """
  def _mark_passing_tones(self):
    ns = self.all_notes()
    L = len(ns)
    range = 10
    for i, n in enumerate(ns):
      pns = n.pitches
      leftpns = []
      for no in ns[max(0, i - range): i]:
        if no.offset + no.duration.quarterLength == n.offset:
          leftpns.extend(no.pitches)
      rightpns = []
      for no in ns[i + 1: min(i + 1 + range, L)]:
        if no.offset == n.offset + n.duration.quarterLength:
          rightpns.extend(no.pitches)
      if self._is_passing(pns, leftpns) and self._is_passing(pns, rightpns):
        n.isPassing = True
      else:
        n.isPassing = False
        

  def _is_passing(self, pns, pms):
    for p in pns:
      found = False
      for q in pms:
        if abs(p.midi - q.midi) <= 2:
          found = True
          break
      if not found:
        return False
    return True

  def _set_dict_from_xml(self, s):
    for p in s.parts:
      for o in p:
        if isinstance(o, stream.Measure):
          n = o.number
          if not self.time_sig:
            self.time_sig = o.timeSignature
          if self.filename in pickups:
            n -= 1
          for name, skip in repeats:
            if self.filename == name and n > skip:
              n -= 1
          if n > 0:
            if not n in self.d:
              self.d[n] = []
            self.d[n].append(o)
            self.measure_nums.append(n)

  def _set_dict_from_krn(self, s):
    for p in s.parts:
      for o in p:
        if isinstance(o, meter.TimeSignature) and not self.time_sig:
          self.time_sig = o
        if isinstance(o, stream.Measure) and self._has_notes(o):
          n = o.number
          if self.filename in pickups:
            n -= 1
          for name, skip in repeats:
            if self.filename == name and n > skip:
              n -= 1
          if n > 0:
            if not n in self.d:
              self.d[n] = []
            self.d[n].append(o)
            self.measure_nums.append(n)
   
  def _has_notes(self, m):
    for o in m:
      if isinstance(o, note.Note) or isinstance(o, chord.Chord):
        return True
      if isinstance(o, stream.Voice):
        return True
    return False

  def _reduce_to_list(self, m):
    result = []
    notes_and_chords = m.flat
    for nc in notes_and_chords:
      result.extend(self._notes_in_object(nc))
    return result 
  
  def _notes_in_object(self, o):

    if isinstance(o, note.Note):
      return [o] 
    if isinstance(o, chord.Chord):
      result = []
      for pit in o.pitches:
        n = note.Note(pit)
        n.duration = o.duration
        result.append(n)
      return result
    if isinstance(o, stream.Voice):
      result = []
      for oo in o:
        result.extend(self._notes_in_object(oo))
      return result
    return []
