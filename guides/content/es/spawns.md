# Lógica de las apariciones en ACB

### Puntuación

Primero el juego asigna una puntuación a cada punto de aparición con el siguiente método:

1. Si la aparición está más cerca que el radio mínimo, se le da una puntuación de 0.
2. Si la aparición está entre el radio mínimo y el radio ideal mínimo, se le da una puntuación entre 0 y 1, siendo 0 en el radio mínimo y 1 en el radio ideal mínimo.
3. Si la aparición está entre los radios ideales mínimo y máximo, se le da una puntuación de 1.
4. Si la aparición está entre el radio ideal máximo y el radio máximo, se le da una puntuación entre 1 y `w`, siendo 1 en el radio ideal máximo y `w` en el radio máximo.
5. Si la aparición está más lejos que el radio máximo, se le da una puntuación de `w`.

Después el juego elige la aparición con la puntuación más alta. Si varias apariciones tienen la misma puntuación, coge la primera con esa puntuación.
Esto hace que ciertas apariciones (por ejemplo el árbol de Florencia o la roja de Siena) salgan favorecidas con mucha frecuencia.

### Parámetros

El método de puntuación se calcula con los siguientes parámetros.

#### Compañero

* Radio mínimo: 4
* Radio ideal mínimo: 5
* Radio ideal máximo: 15
* Radio máximo: 100
* `w`: 0,2

#### Rivales

* Radio mínimo: 30
* Radio ideal mínimo: 40
* Radio ideal máximo: 60
* Radio máximo: 90
* `w`: 0,2 o 0,5 según sea objetivo o perseguidor

### Anfitrión

La lógica de aparición del jugador anfitrión es la misma, pero se ignoran las posiciones de los rivales. En su lugar se usan como posiciones rivales los puntos de muerte (de todos los jugadores del equipo que aún no han reaparecido).
