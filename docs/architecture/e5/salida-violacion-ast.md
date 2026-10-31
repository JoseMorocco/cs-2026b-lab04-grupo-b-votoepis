## Inyección de dependencia prohibida en `elegibilidad.py`

````
python -m pytest -q tests/test_fitness_estructura.py
__________________ test_ff02_adaptadores_no_importan_servicio __________________
    def test_ff02_adaptadores_no_importan_servicio():
E           AssertionError: elegibilidad
FAILED tests/test_fitness_estructura.py::test_ff02_adaptadores_no_importan_servicio - AssertionError: elegibilidad
1 failed, 1 passed in 0.06s
````

## Tras restaurar el archivo

````
..                                                                       [100%]
2 passed in 0.03s
````

## Inyección adicional FF-01 en `dominio.py` (prohibición hacia `externos`)

````
python -m pytest -q tests/test_fitness_estructura.py
_________________ test_ff01_dominio_no_importa_infraestructura _________________
    def test_ff01_dominio_no_importa_infraestructura():
E       AssertionError: assert not ({'abc', 'dataclasses', 'datetime', 'enum', 'src.votacion.estados', 'src.votacion.externos', ...} & {'src.votacion.decoradores', 'src.votacion.elegibilidad', 'src.votacion.eventos', 'src.votacion.externos', 'src.votacion.ia', 'src.votacion.servicio'})
FAILED tests/test_fitness_estructura.py::test_ff01_dominio_no_importa_infraestructura - AssertionError: assert not ({'abc', 'dataclasses', 'datetime', 'enum', 'src.votacion.estados', 'src.votacion.externos', ...} & {'src.votacion.decoradores', 'src.votacion.elegibilidad', 'src.votacion.eventos', 'src.votacion.externos', 'src.votacion.ia', 'src.votacion.servicio'})
1 failed, 1 passed in 0.06s
````

## Ambas violaciones revertidas

````
..                                                                       [100%]
2 passed in 0.03s
````
