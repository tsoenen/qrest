coverage run  --source qrest/  -m unittest discover
coverage report -m
coverage html
firefox htmlcov/index.html &