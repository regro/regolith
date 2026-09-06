**Added:**

* <news item>

**Changed:**

* ``regolith.database`` is a normal Python module.  It was ``database.xsh`` and
  needed the xonsh import hook, which put it beyond the reach of black, flake8,
  isort and docformatter because it was not valid Python.

**Deprecated:**

* <news item>

**Removed:**

* The xonsh dependency.  ``xonsh.api.subprocess`` and ``xonsh.api.os`` are
  replaced by the standard library ``subprocess`` and ``shutil``, and
  ``xonsh.main.setup`` no longer runs on ``import regolith``, which cuts the
  import from about 147 ms to about 47 ms and ``regolith --version`` from about
  1370 ms to about 980 ms.
* The rever dependency, which was unused: there is no ``rever.xsh`` and no
  release workflow invokes it.

**Fixed:**

* ``deploy.py`` and ``storage.py`` can now catch a failing git command.  They
  handle ``subprocess.CalledProcessError``, but ``xonsh.api.subprocess`` does
  not define it, so those handlers raised ``AttributeError`` at the moment a
  git command actually failed.

**Security:**

* <news item>
