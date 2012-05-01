import pynote

"""
Chord object in pymusic
"""
class Chord:

    TEMPLATES = [
        (set([0, 4, 8]), 'augmented triad'),
        (set([0, 4, 7]), 'major triad'),
        (set([0, 3, 7]), 'minor triad'),
        (set([0, 3, 6]), 'diminished triad'),
        (set([0, 4, 7, 10]), 'dominant seventh'),
        (set([0, 3, 7, 10]), 'minor seventh'),
        (set([0, 3, 6, 10]), 'half-diminished seventh'),
        (set([0, 3, 6, 9]), 'fully-diminished seventh'),
        (set([0, 4, 8, 11]), 'augmented seventh')
    ]

    INVERSIONS = ['', '6', '64']
    SEVENTH_INVERSIONS = ['7', '65', '43', '2']

    NUMERAL_CLASSES = [
        [0],
        [2],
        [3, 4],
        [5],
        [7],
        [8, 9],
        [10, 11]
    ]

    NUMERALS = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']

    """
    root: pitch class
    name: string
    inversion: integer (0 root, 1 first inversion, etc)
    pitch_classes = set of pitch classes in chord
    """
    def __init__(self, root, name, inversion, pitch_classes=None):
        self.root = root
        self.name = name
        self.inversion = inversion
        self.pitch_classes = pitch_classes
        
        self.is_seventh = 'seventh' in name
        self.is_major = 'major' in name or 'dominant' in name

        if self.is_seventh:
            self.inversion_name = Chord.SEVENTH_INVERSIONS[inversion]
        else:
            self.inversion_name = Chord.INVERSIONS[inversion]
        
    def __repr__(self):
        return pynote.Note(
            self.root).name + self.inversion_name + ' ' + self.name

    """
    Returns a string representation of this chord as a roman 
    numeral in the given key (pitch class)
    """
    def as_roman(self, key):
      degree = (self.root - key) % 12

      # avoid returning II7 if it should be V7/V
      if 'dominant' in self.name and not degree == 7:
        tonic = (self.root - 7) % 12
        result = self.as_roman(tonic)
        for i, nums in enumerate(Chord.NUMERAL_CLASSES):
          if (tonic - key) % 12 in nums:
            if i == 0:
              return result
            ending = Chord.NUMERALS[i]
            return result + '/' + ending
        return None

      
      for i, nums in enumerate(Chord.NUMERAL_CLASSES):
        if degree in nums:
          s = Chord.NUMERALS[i]
          if not self.is_major:
            s = s.lower()
          if 'diminished' in self.name:
            if 'half' in self.name:
              s = s + '/o'
            else:
              s = s + 'o'
          elif 'augmented' in self.name:
            s = s + '+'    
          s = s + self.inversion_name
          return s
      return None

def from_notes(notes):
    pitch_classes = set([n.pitch_class for n in notes])
    for template, name in Chord.TEMPLATES:
        for k in range(12):
            ps = set([(p - k) % 12 for p in pitch_classes])
            if ps == template:
                root = [n for n in notes if n.pitch_class == k][0]

                bass = min([(n.octave, n.pitch_class) for n in notes])
                bass_pc = (bass[1] - k) % 12
                
                if bass_pc in [3, 4]:
                    inversion = 1
                elif bass_pc in [6, 7, 8]:
                    inversion = 2
                elif bass_pc in [9, 10, 11]:
                    inversion = 3
                else:
                    inversion = 0

                return Chord(root.pitch_class, name, inversion, pitch_classes)
    return None

def from_music21_chord(c):
  if c.isRest:
    return None
  notes = [pynote.from_string(str(p)) for p in c.pitches]
  return from_notes(notes)

def with_slash(s):
  if len(s) < 1:
    return s
  result = [s[0]]
  for i in range(1, len(s)):
    if s[i] in '123456789' and s[i - 1] in '123456789':
      result.append('/')
    result.append(s[i])
  return ''.join(result)


def just_numeral(s):
    i = 0
    while i < len(s) and s[i] in 'ivIV':
        i += 1
    return s[:i]

def just_numeral_with_secondary(s):
  if not '/' in s:
    return just_numeral(s)
  j = s.index('/')
  before = s[:j]
  after = s[j + 1:]
  result = just_numeral(before) + '/' + just_numeral(after)
  if result[-1] == '/':
    return result[:-1]
  return result

"""
Returns the roman numeral s with the slash between the two numbers of the
inversion removed, so that for example ii6/5 becomes ii65
"""
def numeral_reformatted(s):
  for i, c in enumerate(s):
    if c == '/' and 0 < i < len(s) - 1:
      if s[i-1].isdigit() and s[i+1].isdigit():
        return s[:i] + s[i + 1:]
  return s


"""
Returns the number of semitones above the tonic the root
of the chord represented by the given roman numeral is.
Distingushes between major and minor keys for the ambiguous
iii, vi, and vii.  According to tonal harmony, major keys have
iii, vi, and vii, while minor keys have III, VI, and VII.

For example:
V -> 7
iv > 5
vi -> 9
VI -> 8 (since VI occurs in minor)
iii -> 4
"""
def interval_from_tonic(s):
    if not just_numeral(s).upper() in Chord.NUMERALS:
        return None
    degree = Chord.NUMERALS.index(just_numeral(s).upper())
    candidates = Chord.NUMERAL_CLASSES[degree]
    if len(candidates) == 1 or just_numeral(s).isupper():
        return candidates[0]
    else:
        return candidates[1]

"""
Returns True if s is a valid roman numeral string and
False otherwise.
"""
def is_valid_numeral(rn):
    if len(rn) == 0:
        return False
    chars = 'iIvVN+o/234567'
    for i in range(len(rn)):
        if not rn[i] in chars:
            return False
    if not rn[0] in 'ivIVN':
        return False
    return True

def is_augmented(s):
    return '+' in s

"""
Returns True if the roman numeral represents a diminished triad
or a fully-diminished seventh chord
"""
def is_diminished(s):
    if not 'o' in s:
        return False
    i = s.index('o')
    return not (i > 0 and s[i - 1] == '/')

def is_half_diminished(s):
    if not 'o' in s:
        return False
    i = s.index('o')
    return i > 0 and s[i - 1] == '/'

def name_from_pitch_classes(ps):
    for template, name in Chord.TEMPLATES:
        if ps == template:
            return name
    return None

def last_index(s, c):
    for i in range(len(s) - 1, -1, -1):
        if s[i] == c:
            return i
    return None

"""
Returns a chord object corresponding to the given
roman numeral in the given key, or None if the 
roman numeral is malformed.

Allowed roman numerals:

[upper/lower case numeral] [+ | o] [inversion numbers]
"""
def from_numeral_and_key(rn, k):
    last_slash_index = last_index(rn, '/')
    if last_slash_index:
        secondary = rn[last_slash_index + 1:]
        if secondary.upper() in Chord.NUMERALS:
            diff = interval_from_tonic(secondary)
            k = (k + diff) % 12
            rn = rn[:last_slash_index]
    
    
    s = just_numeral(rn)
    root = interval_from_tonic(s)

    if root == None:
        return None

    rest = rn[len(s):]

    inversion_name = ''.join([c for c in rest if c in '234567'])
    
    if s.isupper():
        third = 4
    else:
        third = 3

    if '+' in rest:
        fifth = 8
    elif 'o' in rest:
        fifth = 6
    else:
        fifth = 7
    
        
    if inversion_name in Chord.INVERSIONS:
        inversion = Chord.INVERSIONS.index(inversion_name)
        ps = set([0, third, fifth])
        name = name_from_pitch_classes(ps)
    elif inversion_name in Chord.SEVENTH_INVERSIONS:
        inversion = Chord.SEVENTH_INVERSIONS.index(inversion_name)
        if is_diminished(rn):
            seventh = 9
        elif is_augmented(rn):
            seventh = 11
        else:
            seventh = 10
        ps = set([0, third, fifth, seventh])
        name = name_from_pitch_classes(ps)
    else:
        return None
   
    shifted_ps = set([(x + k + root) % 12 for x in ps])
    root = (root + k) % 12

    return Chord(root, name, inversion, shifted_ps)

