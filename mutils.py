import os

import label
import pychord
import pynote
import section

def num_eighths_in_measure(n, d):
  return n * 8 / d

def no_ext(name):
  name = os.path.basename(name)
  if name.endswith('.krn') or name.endswith('.xml'):
    return name[:-4]  
  return name


def test(name):
  return 'mtest/{0}.txt'.format(no_ext(name))

def sonata(name):
  if '.' in name:
    return name
  return 'mozart/xml/{0}.xml'.format(no_ext(name))

def analysis(name):
  return 'analyses/mozart/{0}.txt'.format(no_ext(name))

def output(name):
  return 'mout/{0}.txt'.format(no_ext(name))

def dmitri_output(name):
  if '.' in name:
    return 'odmout/{0}.txt'.format(no_ext(name))
  return 'dmout/{0}.txt'.format(no_ext(name))

def keys(name):
  return 'mkeys/{0}.txt'.format(no_ext(name))

def save_output(name, labels):
  f = open(output(name), 'w')
  for lab in labels:
    f.write('{0}\n'.format(lab))
  f.close()

def add_slashes(s):
  result = []
  nums = '1234567890'
  for i in range(len(s)):
    result.append(s[i])
    if i < len(s) - 1 and s[i] in nums and s[i + 1] in nums:
      result.append('/')
  return ''.join(result)

def as_dmitri_output(labels):
  result = []
  ck = None
  crn = None
  for i, line in enumerate(labels):
    m, measure = line
    s = 'm' + str(m) + ' '
    for j, p in enumerate(measure):
      rn, k, maj, score = p
      rn = add_slashes(rn)
      if not ck == k or not crn == rn:
        b = 1 + float(j) / 2
        if b == float(int(b)):
          b = int(b)
        if not b == 1:
          s = s +  'b' + str(b) + ' '
        if not ck == k:
          keystr = str(pynote.Note(k))
          if not maj:
            keystr = keystr.lower()
          s = s + keystr + ': '
          ck = k
          s = s + rn + ' '
          crn = rn
        elif not crn == rn:
          s = s + rn + ' '
          crn = rn
    result.append(s)
  return result

def save_dmitri_output(name, labels):
  f = open(dmitri_output(name), 'w')
  f.write('Title: {0}\n'.format(name))
  f.write('Analyzer: Computer program by Jeffrey Hodes\n')
  measure_dur = float(len(labels[0][1])) / 2
  f.write('Measure duration: ' + str(measure_dur) +'\n')
  for line in as_dmitri_output(labels):
    f.write(line + '\n')
  f.close()

def load_output(name):
  if not os.path.exists(output(name)):
    return None
  f = open(output(name), 'r')
  result = []
  for line in f.readlines():
    result.append(label.from_string(line))
  return result

def load_keys(name):
  f = open(keys(name), 'r')
  result = []
  for line in f.readlines():
    fields = line.split()
    pair = fields[0].split('-')
    result.append((int(pair[0]), pair[1] == 'True'))
  return result


"""
Loads the lists of section templates from its location on disk,
given as a pair (major, minor)
"""
def load_sectionaries():
  return (load_sectionary('sectiontemplates/major.txt'),
    load_sectionary('sectiontemplates/minor.txt'))
  
def load_sectionary(filename):
  result = []
  f = open(filename)
  sections = f.read().split('\n\n')
  for gp in sections:
    s = section.from_string(gp)
    if s:
      result.append(s)
  return result

"""
Converts a list of sections into a list of measures, each of which is a
list of eighth beats
"""
def as_labeling(labels):
  measure_len = max([lab.stop_int for lab in labels])
  measure_nums = sorted(list(set([lab.measure for lab in labels])))
  result = []
  for m in measure_nums:
    measure = [None for i in range(measure_len)]
    labs = [lab for lab in labels if lab.measure == m]
    for lab in labs:
      for i in range(lab.start_int, lab.stop_int):
        measure[i] = (lab.rn, lab.key, lab.major, lab.score)
    result.append((m, measure))
  
  for m, measure in result:
    for i, p in enumerate(measure):
      if not p:
        if i > 0:
          measure[i] = measure[i - 1]
  return result
 
