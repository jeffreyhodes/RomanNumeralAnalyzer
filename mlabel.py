import sys
import os

import efficient
import label
import menumerate
import mkeys
import mmarkov
import mutils
import refinements
import section

def get_section_size_bound(n):
  if n == 3:
    return 4
  else:
    return n

def min_with_tiebreak(pairs):
  s, section = min(pairs)
  choices = [(len(sec.rn), sec) for sc, sec in pairs if sc - s < 0.000001]
  length, result = min(choices)
  return (s, result)

def label_measure(es, labels, model, mark_len, prev_lab):
  chosen_labels = []
  
  # weight associated with markov model
  markov_factor = 0.8
  
  x = []
  for lab in labels:

    if lab.start == 0 and lab.stop_int < get_section_size_bound(mark_len):
      if prev_lab:
        if prev_lab.key == lab.key:
          x.append((lab.score + markov_factor * (
            1 - model.score(prev_lab.rn, lab.rn)), lab))
        else:
          x.append((lab.score, lab))
      else:
        x.append((lab.score, lab))
  sc, cur = min_with_tiebreak(x)
  chosen_labels.append(cur)
  pos = cur.stop_int

  while pos < mark_len:
    choices = []
    for lab in labels:
      if lab.start_int in [pos]:
        choices.append((lab.score + markov_factor * (
            1 - model.score(cur.rn, lab.rn)), lab))
    dist, choice  = min_with_tiebreak(choices)
    if dist < 100:
      chosen_labels.append(choice)
      pos = choice.stop_int
      cur = choice
    else:
      pos += 1

  return chosen_labels

def label_measure_basic(es, labels, model, mark_len, prev_lab):
  result = []
  mark = [None] * mark_len
  for s in labels:
    mark, dirty = add(s, mark)
    if dirty:
      result.append(s)
  return result

"""
Adds the given section to the given measure analysis, filling in all 
beats that heven't yet been filled
"""
def add(section, measure):
  dirty = False
  result = measure[:]
  for i in range(section.start_int, section.stop_int):
    if not result[i]:
      result[i] = (section.rn, section.key)
      dirty = True
  return result, dirty

"""
labels the given sonata represented as a measure dictionary, returning
a list of lists of pairs (rn, k), one for each 8th note in each
measure
"""
def label_piece(es, sectionaries, keylist, model, single=None):
  labels = []
  ts = es.time_sig
  to_check = menumerate.sections_to_check(ts.numerator, ts.denominator)
  mark_len = int(round(2 * max([b for a, b in to_check])))
  prev_label = None

  base_index = 0

  for m in es.measure_nums:
    if not single == None:
      m = single
      es.show_measure(m)
    results = []
    for start, stop in to_check:
      if not single == None:
        index = (m - 1) * mark_len + int(round(start * 2))
      else:
        index = base_index + int(round(start * 2))
      k, maj = keylist[index]
      if maj:
        sectionary = sectionaries[0]
      else:
        sectionary = sectionaries[1]
      notes = es.notes_in_measure(m, start, stop)
      nsec = section.from_notes(notes, k)
      pairs = [(sec.distance(nsec), sec.numeral) for sec in sectionary]
      choices = [label.Label(
        s, m, start, stop, k, maj, rn) for s, rn in pairs]
      results.extend(sorted(choices, key=lambda x: x.score)[:3])
    results.sort(key=lambda x: x.score)
    new_labels= label_measure(es, results, model, mark_len, prev_label)
    prev_label = new_labels[-1]
    labels.extend(new_labels)
    base_index += mark_len
    if not single == None:
      print((k, maj))
      for r in results:
        print(r)
      return 
 
  labels = refinements.fill_gaps(labels)
  labels = refinements.fix_prefixes(labels)
  labels = refinements.fix_triples(labels, es)
  labels = refinements.join_adjacents(labels)
  labels = refinements.fix_inversions(labels, es)
  labels = refinements.rename_errors(labels)
  labels = refinements.fix_common_errors(labels, es)
  labels = refinements.fix_Vs(labels, es)
  labels = refinements.fix_basses(labels, es)

  return labels

def main():
  key_model = mkeys.hmm_from_training_dir()
  model = mmarkov.from_file('transitionmodels/model.txt')
  sectionaries = mutils.load_sectionaries()
  
  single = None
  names = sys.argv[1:]
  if sys.argv[1][0] == '-':
    single = int(sys.argv[1][1:])
    names = names[1:] 
  
  for name in names:
      es = efficient.EfficientScore(mutils.sonata(name))
      outputs = es.output_string_list()
      keylist = map(mkeys.extract_pair, key_model.most_likely_sequence(outputs))
     
      if not single == None:
        label_piece(es, sectionaries, keylist, model, single=single)
      else:
        sections = label_piece(es, sectionaries, keylist, model)
        if len(names) < 2:
          for line in mutils.as_dmitri_output(mutils.as_labeling(sections)):
            print(line)

if __name__ == '__main__':
  main()
