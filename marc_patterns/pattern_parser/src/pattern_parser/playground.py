pattern = "publish on year, month, day every day but omit saturday"

def tail_n_head(string, separator=","):
  # guaranteed to return a tuple of two parts
  # if only one part, then the first part is empty
  if string:
    head_tail = string.split(separator, 1)
    if len(head_tail) == 1:
      return ["", head_tail[0]]
    else:
      return head_tail
  else:
    return ["",""]


pattern = pattern[7:]
