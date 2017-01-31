# Poppy Creature

[![PyPI](https://img.shields.io/pypi/v/poppy-creature.svg)](https://pypi.python.org/pypi/poppy-creature/)

## Migration notes for v2.0.0

The poppy-creature package is now integrated in [pypot](https://github.com/poppy-project/pypot)>=3, and v2.0.0 is a placeholder only kept for compatibility.

You should fix your imports from:

```python
# old import
from poppy.creatures import PoppyErgoJr
```

to

```python
# new import
from pypot.creatures import PoppyErgoJr
```
