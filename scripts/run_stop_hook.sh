#!/usr/bin/env bash

python3 scripts/test_execute.py
status=$?

if [ $status -ne 0 ]; then
  echo "Stop hook failed: scripts/test_execute.py exited with status $status" >&2
fi

exit $status