# podrobný popis skriptu

Python skript pro automatizované zpracování a analýzu měřicích `.hdf5` souborů obsahujících signály `S0`, `S1`, `S2`, `S3` a `Bal`.

Skript umožňuje:

* načtení a předzpracování signálů,
* normalizaci dat,
* vyhlazení průběhů,
* výpočet hodnoty DOP,
* automatickou segmentaci měření na fáze `Klid` / `Stisk`,
* generování PDF grafů,
* export výsledků do CSV souborů.

---

# Formát vstupních souborů

Skript očekává `.hdf5` soubory obsahující datasety:

```text
S0
S1
S2
S3
Bal
```

Vzorkovací frekvence musí být uvedena v názvu souboru.

Příklad:

```text
001-test_1000.hdf5
```

kde:

```text
1000 = fs
```

---

# Použité knihovny

* h5py
* pandas
* numpy
* matplotlib
* scipy.signal

---

# Funkce skriptu

## Zpracování signálů

Skript:

1. Načte `.hdf5` soubor.
2. Ořízne neplatná data na konci měření.
3. Normalizuje signály:

```python
S1 / S0
S2 / S0
S3 / S0
```

4. Vyhladí signály pomocí Savitzky-Golay filtru.
5. Spočítá hodnotu DOP:

```python
DOP = sqrt(S1² + S2² + S3²)
```

6. Vytvoří grafy a exportuje výsledky.

---

# Struktura složek

Projekt očekává následující strukturu:

```text
projekt/
│
├── parcelingSOP.py
├── vstupSOP/
│   ├── soubor1.hdf5
│   ├── soubor2.hdf5
│   └── ...
│
└── vystupSOP/
```

## Vstupní složka

```text
vstupSOP
```

Obsahuje `.hdf5` soubory určené ke zpracování.

## Výstupní složka

```text
vystupSOP
```

Skript ji automaticky vytvoří, pokud neexistuje.

---

# Podporované režimy

## Režim 1 — Rameno

Kompletní analýza s automatickým hledáním výrazných změn během měření.

### Funkce režimu:

* detekce fází `Klid` a `Stisk`,
* segmentace signálu `Bal`,
* barevné zvýraznění fází v grafech,
* výpočet mediánů pro jednotlivé segmenty,
* export detailních CSV výsledků.

### Generované soubory

```text
VYSLEDKY_MASTER.csv
VYSLEDKY_BAL.csv
VYSLEDKY_DOP.csv
VYSLEDKY_VEKTORY.csv
```

---

## Režim 2 — Ostatní

Jednodušší režim bez segmentace.

### Funkce režimu:

* vytvoření grafů,
* výpočet celkových průměrů,
* výpočet směrodatných odchylek.

### Generovaný soubor

```text
Prumery_komplet.csv
```

---

# Segmentace signálu

V režimu `Rameno` skript automaticky rozpoznává:

* klidové části měření,
* aktivní části měření (`Stisk`).

Detekce probíhá na základě:

* adaptivního prahování,
* odhadu šumu,
* vyhlazení binární masky,
* filtrování krátkých segmentů.

---

# Generované grafy

Pro každý soubor vzniká PDF obsahující:

1. průběhy `S1`, `S2`, `S3`,
2. průběh `DOP`,
3. průběh `Bal`.

V režimu `Rameno` jsou navíc barevně označeny jednotlivé fáze:

* zelená = `Klid`
* červená = `Stisk`

---

# Požadované knihovny

Instalace závislostí:

```bash
pip install h5py pandas numpy matplotlib scipy
```

---

# Spuštění skriptu

```bash
python parcelingSOP.py
```

Po spuštění program nabídne výběr režimu:

```text
1 - Rameno
2 - Ostatní
```
