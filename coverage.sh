coverage run  --source rest_client/  -m unittest discover
coverage report -m
coverage html
firefox htmlcov/index.html &