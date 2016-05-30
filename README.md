SHRDR - A parallel test runner for gtest
========================================

`shrdr` is a parallel test runner for gtest. It uses gtest's included support
for sharding. Tests are run in parallel on the same machine.

Synopsis
--------

```
Usage: shrdr.py [options] <test> [-- <test_options>]

Options:
  -h, --help            show this help message and exit
  -j jobs, --jobs=JOBS
                        number of workers to spawn. DEFAULT: nproc*1.5
  -v VERBOSITY, --verbosity=VERBOSITY
                        output verbosity: 0 only shows summarized information,
                        1 also shows full logs of failed shards, and anything
                        >1 shows all output. DEFAULT: 1
```


Open issues
-----------

- [ ] Add a verbosity level 3 which prints logs as they come in (in a thread-safe way)
- [ ] Add support for providing a matcher for tests which cannot be run in parallel. These would be filtered from the parallel stage and run in isolation.

