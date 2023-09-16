#!bin.bash

python -m twine upload --config-file .pypirc --repository "$1" dist/*