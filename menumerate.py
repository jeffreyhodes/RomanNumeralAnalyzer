"""
Returns a list of all possible labelings of a measure containing length
eighth notes using elements of sections
"""
def all_labelings(sections, length):
  return get_labelings(sections, 0, length)

def get_labelings(sections, a, b):
  if len(sections) == 0:
    return []
  if a >= b:
    return []
  
  result = []
  for i, s in enumerate(sections):
    score, m, start, stop, k, rn = s
    ap = int(round(start * 2))
    bp = int(round(stop * 2))
    if ap < a or bp > b:
      continue
    remains = sections[:]
    remains.remove(s)
    
    left = get_labelings(remains, a, ap)
    right = get_labelings(remains, bp, b)
    
    if len(left) == 0 and len(right) == 0:
      result.append([s])
    else:
      for L in left:
        for R in right:
          result.append(L + [s] + R)
  
  return result 

"""
Returns a list of all pairs of elements in sections
that are adjacent in time ordered by Markov likelihood
"""
def form_ordered_pairs(sections, model):
  result = []
  for a in sections:
    for b in sections:
      (s1, m1, start1, stop1, k1, rn1) = a
      (s2, m2, start2, stop2, k2, rn2) = b
      if stop1 == start2:
        score = model.score(rn1, rn2)
        if score > 0:
          result.append(
            ((((s1 + s2) / 2 +  1 - model.score(rn1, rn2)) / 2), (a, b)))
  return sorted(result)

def sections_to_check(n, d):
  if d == 2:
    return sections_to_check(2 * n, 2 * d)
  if d == 8:
    if n == 1:
      return [(0.0, 0.5)]
    elif n == 3:
      p = sections_to_check(n / 3, d)
      return p + shifted(p, 0.5) + shifted(p, 1) + [(0.0, 1.5)]
    else: # n == 6
      p = sections_to_check(n / 2, d)
      return p + shifted(p, 1.5) + [(0.0, 3.0)]
  else: # d == 4
    if n == 1:
      p = sections_to_check(n, 2 * d)
      return p + shifted(p, 0.5) + [(0.0, 1.0)]
    elif n == 2 or n == 4:
      p = sections_to_check(n / 2, d)
      return p + shifted(p, n / 2) + [(0.0, float(n))]
    else: # n == 3
      p = sections_to_check(n / 3, d)
      return p + shifted(p, 1.0) + shifted(p, 2.0) + [(0.0, 3.0)]

def shifted(pairs, t):
  return [(a + t, b + t) for a, b in pairs]
