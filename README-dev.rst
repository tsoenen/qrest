For developers of qrest
***********************

If you want to work on qrest itself, you are advised to use a virtualenv to
install its dependencies and the required Python development tools. You can let
the Python tool tox_ create one for you or create one yourself. Note that tox
also configures several commands for you, e.g. to run the style-guide checker or
to run the coverage tool. If you create the virtualenv manually, you have to
invoke the underlying tools yourself.

The next two subsections describe how to create the virtualenv either through
tox or manually. The third subsection describes the most important development
tools that the virtualenv provides.

Let tox create the virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section assumes tox has already been installed and command ``tox`` is
available from the command line. tox automates all kinds of developer actions
for you and automatically creates the virtualenv that they require. For example,
if you execute the following command::

  $ tox -e py37-test

tox automatically configures a virtualenv in subdirectory ``.tox/py37-dev`` (in
the project root directory) and uses it to run the unit tests. If you execute
``tox`` again, it will reuse that same virtualenv and not create a new one.

You can use the virtualenv yourself. To activate it, execute the following
command::

    $> source .tox/py37-dev/bin/activate
    (py37-dev) $>

Create virtualenv yourself
~~~~~~~~~~~~~~~~~~~~~~~~~~

The commands in this section have to be executed from the root of the repo.

To create a virtualenv named py37-dev, execute the following command::

    $ python -m venv py37-dev

This virtualenv contains a Python environment with a minimal amount of packages.
To install the packages that are required for development, you first have to
activate the virtualenv::

    $ source py37-dev/bin/activate
    (py37-dev) $

The command prompt shows the name of the active virtualenv, which is a feature
of most interactive shells.

The file ``requirements.txt`` specifies all the development dependencies and
their exact version. The Python installer ``pip`` can read this file and install
the packages it lists::

    (py37-dev) $> pip install -r requirements.txt

Available development commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section we describe some of the developer tools that are available when
you install the contents of the requirements file. You can call these tools from
the command-line or let tox do that for you. The table at the end of this
section shows how to call the either way.

The Python code in this repo should remain PEP8_-compliant, that is, it should
adhere to the official Python style guide. The development virtualenv provides
the following tools to assist with that:

- black_ to automatically format Python code in a PEP8-compliant way;
- flake8_ to verify your code is PEP8-compliant;

flake8 might seems superfluous when you also have black. However it finds cases
not (yet) covered by black and does some other thing, e.g., warn for unused
imports and variables. Furthermore, most IDEs can execute flake8 "in the
background" and inform you of any violations while you type.

pytest_ is available to collect and run the unit tests. It has more
functionality than plain ``unittest``, such as a more extensive configurability
of test selection and test output. It's compatible to the standard ``unittest``.

coverage_ is available to compute the coverage and show a report in plain text
or as a set of HTML pages that allow you to navigate to the file(s) of interest.

The following table lists the command to use the aforementioned tools:

=========== =========================== ============================================================
Tool to run Using tox                   Using active virtualenv
=========== =========================== ============================================================
black       ``$> tox -e py37-black``    ``(py37-dev) $> black setup.py qrest test``
coverage    ``$> tox -e py37-coverage`` ``(py37-dev) $> coverage run --source=qrest,test -m pytest``
flake8      ``$> tox -e py37-flake8``   ``(py37-dev) $> flake8 setup.py qrest test``
pytest      ``$> tox -e py37-test``     ``(py37-dev) $> pytest``
=========== =========================== ============================================================

The exact specification of the tox commands can be found in file ``tox.ini`` in
the project root directory.

.. _black: https://black.readthedocs.io/en/stable/
.. _coverage: https://coverage.readthedocs.io/en/coverage-5.1/
.. _flake8: https:://flake8.pycqa.rog/en/latest/
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _pytest: https://docs.pytest.org/en/stable/index.html
.. _tox: https://tox.readthedocs.io/en/latest/
