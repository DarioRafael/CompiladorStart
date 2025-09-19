# -*- coding: utf-8 -*-
# intermediate_code/__init__.py

"""
Módulo de generación de código intermedio para el compilador Java
Contiene clases para generar triplos y cuádruplos
"""

from .generador_triplos import GeneradorTriplos, Triplo
from .generador_cuadruplos import GeneradorCuadruplos, Cuadruplo

__all__ = [
    'GeneradorTriplos',
    'Triplo',
    'GeneradorCuadruplos',
    'Cuadruplo'
]

__version__ = '1.0.0'
__author__ = 'Compilador Java Team'