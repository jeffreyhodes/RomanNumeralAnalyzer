import pychord
import section

"""
Methods that act on lists of sections to make them better
"""

def fill_gaps(labels):
  measure_len = max([lab.stop_int for lab in labels])
  result = []
  for s1, s2 in zip(labels, labels[1:]):
    if s2.measure > s1.measure:
      if s1.stop_int < measure_len:
        s1.set_stop(float(measure_len) / 2)
        result.append(s1)
      else:
        result.append(s1)
    else:
      if s1.stop == s2.start:
        result.append(s1)
      else:
        s1.set_stop(s2.start)
        result.append(s1)
  result.append(labels[-1])
  return result

def join_adjacents(labels):
  result = labels[:]
  toremove = []
  N = len(result)
  for i in range(N):
    if i < N - 1:
      a = result[i]
      b = result[i + 1]
      if a.measure == b.measure and a.rn == b.rn:
        a.stop = b.stop
        a.stop_int = b.stop_int
        toremove.append(b)
        result[i] = a

  for s in toremove:
    result.remove(s)
  return result

def fix_prefixes(labels):
  result = labels[:]
  N = len(result)
  for i in range(N):
    if i < N - 1:
      a = result[i]
      b = result[i + 1]
      rn1 = a.rn
      rn2 = b.rn
      srn2 = pychord.just_numeral_with_secondary(rn2)
      if rn1 == 'ii2' and rn2 == 'I':
        a.rn = 'I'
      if rn1 == 'ii7':
        a.rn = 'I6'
      result[i] = a
      result[i+1] = b
  return result



def fix_vii_to_V(labels):
  result = labels[:]
  N = len(result)
  for i in range(N):
    if i < N - 1:
      a = result[i]
      b = result[i + 1]
      rn1 = a.rn
      rn2 = b.rn
      srn1 = pychord.just_numeral_with_secondary(rn1)
      srn2 = pychord.just_numeral_with_secondary(rn2)
      if srn1 == 'V' and srn2 == 'vii':
        b.rn = rn1
      if srn2 == 'V' and srn1 == 'vii':
        a.rn = rn2
      result[i] = a
      result[i+1] = b
  return result



def fix_common_errors(labels, es):
  result = labels[:]
  N = len(result)
  for i in range(N):
    if i < N - 1:
      a = result[i]
      b = result[i + 1]
      rn1 = a.rn
      rn2 = b.rn
      srn2 = pychord.just_numeral_with_secondary(rn2)
      if rn2 in ['I', 'I6', 'i', 'i6']:
        notes = es.notes_in_measure(a.measure, a.start, a.stop)
        ps = set([n.pitch.pitchClass for n in notes])
        if (11 + a.key) % 12 in ps:
          if rn1 == 'ii':
            a.rn = 'viio6'
          if rn1 == 'iio65':
            a.rn == 'viio43'
      result[i] = a
      result[i+1] = b
  return result



def fix_inversions(labels, es):
  result = labels[:]
  N = len(result)
  for i in range(N):
    if i < N - 1:
      a = result[i]
      b = result[i + 1]
      rn1 = a.rn
      rn2 = b.rn
      srn1 = pychord.just_numeral_with_secondary(rn1)
      srn2 = pychord.just_numeral_with_secondary(rn2)
      if srn1.lower() == srn2.lower() and not rn1 == rn2:
        anotes = es.notes_in_measure(a.measure, a.start, a.stop)
        bnotes = es.notes_in_measure(b.measure, b.start, b.stop)
        abass = min(anotes, key=lambda x: x.pitch.midi).pitch.midi
        bbass = min(bnotes, key=lambda x: x.pitch.midi).pitch.midi
        if abass + 6 < bbass or abass == bbass:
          b.rn = a.rn
        if bbass + 11 < abass and ('64' in rn1 or '6/4' in rn1):
          a.rn = b.rn
      result[i] = a
      result[i+1] = b
  return result

renames = {
  'V/iv': 'I',
  'V/IV': 'I',
  'V6/IV': 'I6'
}

def rename_errors(labels):
  result = [] 
  for lab in labels:
    if lab.rn in renames:
      lab.rn = renames[lab.rn]
    result.append(lab)
  return result

basses = [
  ('I64', 0, 'I')
]

def fix_basses(labels, es):
  result = []
  for lab in labels:
    for a, d, b in basses:
      if lab.rn == a:
        notes = es.notes_in_measure(lab.measure, lab.start, lab.stop)
        bass = min(notes, key=lambda x: x.pitch.midi).pitch.pitchClass
        if (bass - lab.key) % 12 == d:
          lab.rn = b
    result.append(lab)
  return result 

def fix_Vs(labels, es):
  result = []
  for lab in labels:
    if lab.rn == 'V':
      notes = es.notes_in_measure(lab.measure, lab.start, lab.stop)
      ps = [n.pitch.pitchClass for n in notes]
      if (5 + lab.key) % 12 in ps:
        lab.rn = 'V7'
    if lab.rn == 'V7':
      notes = es.notes_in_measure(lab.measure, lab.start, lab.stop)
      ps = [n.pitch.pitchClass for n in notes]
      if not (5 + lab.key) % 12 in ps:
        lab.rn = 'V'
    if lab.rn == 'viio64':
      notes = es.notes_in_measure(lab.measure, lab.start, lab.stop)
      ps = [n.pitch.pitchClass for n in notes]
      if (7 + lab.key) % 12 in ps or True:
        lab.rn = 'V2'
    result.append(lab)
  return result

def fix_triples(labels, es):
  result = labels[:]
  N = len(labels)
  triples = {
    ('I64', 'ii65', 'I6') : 'V2',
    ('I', 'ii2', 'I') : 'I'
  }
  for i in range(N):
    if i < N - 2:
      rn1 = result[i].rn
      rn2 = result[i + 1].rn
      rn3 = result[i + 2].rn

      t = (rn1, rn2, rn3) 
      if t in triples:
        result[i + 1].rn = triples[t]

      st = map(pychord.just_numeral_with_secondary, t)
  return result
 
