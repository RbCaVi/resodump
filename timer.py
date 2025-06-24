import contextlib
import time

@contextlib.contextmanager
def timer(tag):
  start = time.time()
  print(tag, 'start')
  yield
  print(tag, f'end - {time.time() - start} seconds')