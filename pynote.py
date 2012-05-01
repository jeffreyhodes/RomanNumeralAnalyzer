"""
Basic note object in pymusic
"""

class Note:

    NAMES = {
        'C': 0,
        'D': 2,
        'E': 4,
        'F': 5,
        'G': 7,
        'A': 9,
        'B': 11
    }

    def __init__(self, pitch_class, octave=None):
        self.pitch_class = pitch_class
        self.octave = octave
        
        cp = min([(abs(pitch_class - Note.NAMES[c]), c) for c in Note.NAMES])
        name = cp[1]
        if pitch_class == Note.NAMES[name] - 1:
            name = name + 'b'
        elif pitch_class == Note.NAMES[name] + 1:
            name = name + '#'

        if name == 'D#':
          name == 'Eb'
        if name == 'A#':
          name = 'Bb'

        self.name = name
    
    def __repr__(self):
        s = self.name
        if self.octave or self.octave == 0:
            s = s + str(self.octave)
        return s

"""
Makes a Note from a string that has:
1) letter name
2) some sharps and/or flats
3) an octave (optional)
so valid strings are C, Ab4, A##b
"""
def from_string(s):
    name = s[0].upper()
    num_flats = len([c for c in s[1:] if c in '-b'])
    num_sharps = len([c for c in s[1:] if c in '#s'])

    i = len(s) - 1
    while i >= 0 and s[i] in '0123456789':
        i -= 1

    if i < len(s) - 1:
        octave = int(s[i + 1:])
    else:
        octave = None
    
    return Note((Note.NAMES[name] - num_flats + num_sharps) % 12, octave)
