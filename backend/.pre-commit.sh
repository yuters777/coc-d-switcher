   #!/bin/bash
   pytest tests/test_basic.py tests/test_api_simple.py -q
   if [ $? -ne 0 ]; then
     echo "Tests failed - commit aborted"
     exit 1
   fi