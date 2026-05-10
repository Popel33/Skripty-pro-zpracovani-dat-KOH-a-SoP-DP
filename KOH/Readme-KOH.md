# Optical Measurement Processing Tool

Python program pro zpracování měřicích `.perf` souborů obsahujících optické parametry.  
Program načítá data, filtruje vybrané parametry, provádí vyhlazení signálu, vytváří PDF grafy a generuje statistické výstupy ve formátu CSV.

---

# Funkce programu

Program umožňuje:

- načítání `.perf` souborů,
- filtrování vybraných parametrů,
- převod dat do tabulkové struktury,
- vyhlazení signálu pomocí mediánového filtru,
- automatickou detekci fází **Klid / Síla**,
- výpočet statistik,
- export grafů do PDF,
- export výsledků do CSV,
- srovnání více měření v jednom PDF.

---

# Podporované parametry

Program zpracovává pouze následující parametry:

- `Opt rcv pwr`
- `Q factor`
- `Signal to noise ratio`
- `Fec ber`

---

# Struktura složek

Projekt očekává následující strukturu:

```text
projekt/
│
├── parcelingKOH_final.py
├── vstup/
│   ├── soubor1.perf
│   ├── soubor2.perf
│   └── ...
│
└── vystup/
```

## `vstup`

Do této složky vložte všechny `.perf` soubory určené ke zpracování.

## `vystup`

Program sem automaticky ukládá:

- PDF grafy,
- CSV statistiky,
- souhrnné výsledky.

Pokud složka neexistuje, program ji vytvoří automaticky.

---

# Instalace

## Požadavky

Python 3.9 nebo novější.

## Instalace knihoven

```bash
pip install pandas matplotlib numpy
```

---

# Spuštění programu

Program spusťte příkazem:

```bash
python parcelingKOH_final.py
```

Po spuštění se zobrazí nabídka:

```text
1: Rameno (detekce fází Klid/Síla)
2: Ostatní (pouze celkové průměry a odchylky)
```

---

# Režimy programu

## 1. Rameno — detekce fází Klid / Síla

Tento režim slouží pro měření, kde dochází ke střídání:

- klidové fáze,
- působení síly.

Program:

1. analyzuje parametr `Opt rcv pwr`,
2. automaticky určí rozhodovací práh,
3. rozdělí data na jednotlivé fáze,
4. vypočítá mediánové hodnoty parametrů pro každou fázi.

### Výstupy

Program vytvoří:

- PDF grafy pro každý soubor,
- CSV s vyčištěnými daty,
- souhrnný soubor:

```text
souhrnne_statistiky.csv
```

---

## 2. Ostatní — průměry a odchylky

Tento režim neprovádí detekci fází.

Program pouze počítá:

- celkový průměr,
- směrodatnou odchylku.

### Výstupy

Pro každý soubor:

```text
nazevsouboru_prumer.csv
```

Souhrnný výstup:

```text
souhrn_vsech_prumeru.csv
```

---

# Zpracování dat

Program:

1. načte data ze `.perf` souborů,
2. pomocí regulárního výrazu vyhledá relevantní záznamy,
3. vytvoří tabulku měření,
4. převede čas na sekundy,
5. převede hodnoty na numerická data,
6. provede mediánové vyhlazení signálu.

## Vyhlazení dat

Používá se:

- rolling median,
- okno o velikosti 11 hodnot.

Tím se redukuje šum a krátkodobé výkyvy měření.

---

# Generování grafů

Program automaticky vytváří PDF grafy všech parametrů.

Každý vstupní `.perf` soubor má vlastní PDF:

```text
soubor.pdf
```

Obsahuje:

- časovou osu,
- průběh jednotlivých parametrů,
- logaritmickou osu pro `Fec ber`.

---

# Srovnání všech měření

Po dokončení program vytvoří:

```text
srovnani_vsech_mereni.pdf
```

Tento soubor obsahuje porovnání všech měření v jednom dokumentu.

Každý parametr má vlastní srovnávací graf.

---

# Princip detekce fází

Detekce fází využívá parametr:

```text
Opt rcv pwr
```

Program:

1. vypočítá mediánový průběh,
2. určí 10% a 90% kvantil,
3. vytvoří rozhodovací práh,
4. rozdělí data na:

- Klid,
- Síla.

Krátké segmenty jsou odstraněny jako šum.

---

# Výstupní soubory

## PDF

- individuální grafy měření,
- srovnávací grafy všech měření.

## CSV

- vyčištěná data,
- statistiky jednotlivých měření,
- souhrnné statistiky.

---

# Ošetření chyb

Program kontroluje:

- existenci složky `vstup`,
- přítomnost `.perf` souborů,
- chyby při čtení souborů,
- neočekávané chyby během běhu.

V případě problému vypíše chybovou hlášku místo okamžitého ukončení.

---

# Použité knihovny

- pandas
- matplotlib
- numpy
- re
- os
- sys

---

# Autor

Interní nástroj pro analýzu optických měření a automatické generování statistik.
