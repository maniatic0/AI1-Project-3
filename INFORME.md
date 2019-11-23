# Informe III: SAT y Nonogramas

## Integrantes

* Christian Oliveros 13-11000
* Yuni Quintero 14-10880

## Resultados


| Nonograma / Metodos |      Heule      |        Logaritmico       |
|:--------:|:------------------:|:------------------:|
|     42![42](pngs/42.png "42")    | Number of variables: 41725, Number of clauses: 145082, Parse time: 0.06 s   | Number of variables: 22381, Number of clauses: 400274, Parse time: 0.11 s  |
|     94![94](pngs/94.png "94")    | Number of variables: 64042, Number of clauses: 272326, Parse time: 0.07 s | Number of variables: 34070, Number of clauses: 702602, Parse time: 0.15 s |
|     101![101](pngs/101.png "101")    | Number of variables: 65158, Number of clauses: 282398, Parse time: 0.08 s | Number of variables: 34655, Number of clauses: 720297, Parse time: 0.14 s |
|     108![108](pngs/108.png "108")    | Number of variables: 70862, Number of clauses: 249122, Parse time: 0.09 s | Number of variables: 37645, Number of clauses: 725983, Parse time: 0.17 s |
|     123![123](pngs/123.png "123")    | Number of variables: 57098, Number of clauses: 229510, Parse time: 0.08 s | Number of variables: 30430, Number of clauses: 612354, Parse time: 0.15 s |
|     133![133](pngs/133.png "133")    | Number of variables: 55362, Number of clauses: 264290, Parse time: 0.07 s | Number of variables: 29520, Number of clauses: 635276, Parse time: 0.15 s |
|     candle![candle](pngs/candle.png "candle")    | Number of variables: 11000, Number of clauses: 39726, Parse time: 0.01 s | Number of variables: 6125, Number of clauses: 85601, Parse time: 0.02 s |
|     flower![flower](pngs/flower.png "flower")    | Number of variables: 63174, Number of clauses: 279998, Parse time: 0.10 s | Number of variables: 33615, Number of clauses: 704345, Parse time: 0.15 s |

Se puede observar que el metodo Heule da resultados mas optimos que Logaritmico conr especto a parse time. Tambien en el caso del numero de clausulas expuestas en la tabla. Por otro lado, heule utiliza una mayor cantidad de variables justamente para agilizar el computo.