# Zpracování HTML tabulek do Excelu

Tento projekt obsahuje dva Python skripty pro automatické zpracování dat z HTML souborů.  
První skript extrahuje tabulky z HTML souborů a ukládá je do Excel souborů.  
Druhý skript následně vybere konkrétní části těchto Excel souborů, spojí je do listu `Komplet` a vytvoří finální soubor `vse_komplet.xlsx`.

---

## Funkce skriptů

### `parceling1.py`

Skript slouží k načtení HTML souborů ze složky `vstupni_data`, vyhledání všech HTML tabulek a jejich uložení do Excel souborů.

Každá nalezená tabulka je uložena do samostatného listu v Excelu s názvem:

```text
Table_1
Table_2
Table_3
...
```

Výsledné Excel soubory jsou uloženy do složky `vystupni_data`.

---

### `cisteni_upr.py`

Skript pracuje s Excel soubory ve složce `vystupni_data`.

Pro každý `.xlsx` soubor:

1. otevře Excel soubor,
2. odstraní starý list `Komplet`, pokud už existuje,
3. vytvoří nový list `Komplet`,
4. z vybraných listů `Table_X` zkopíruje pouze určené rozsahy řádků,
5. odstraní původní listy `Table_1` až `Table_21`,
6. uloží upravený soubor s prefixem `upraveno_`,
7. nakonec všechny listy `Komplet` spojí do jednoho souboru:

```text
vystupni_data/vse_komplet.xlsx
```

---

## Struktura složek

Doporučená struktura projektu:

```text
projekt/
│
├── parceling1.py
├── cisteni_upr.py
│
├── vstupni_data/
│   ├── soubor1.html
│   ├── soubor2.html
│   └── ...
│
└── vystupni_data/
    ├── soubor1.xlsx
    ├── soubor2.xlsx
    ├── upraveno_soubor1.xlsx
    ├── upraveno_soubor2.xlsx
    └── vse_komplet.xlsx
```

---

## Použité knihovny a jejich instalace

Projekt používá tyto Python knihovny:

- `os` – práce se soubory a složkami, součást Pythonu
- `re` – přirozené řazení názvů souborů, součást Pythonu
- `BeautifulSoup` – parsování HTML
- `pandas` – práce s tabulkami
- `openpyxl` – čtení a zápis Excel souborů

Instalace potřebných knihoven:

```bash
pip install beautifulsoup4 pandas openpyxl
```

---

## Spuštění

### 1. Vložení HTML souborů

Nejprve vložte vstupní HTML soubory do složky:

```text
vstupni_data
```

Pokud složka neexistuje, vytvořte ji ručně.

---

### 2. Spuštění prvního skriptu

Spusťte skript:

```bash
python parceling1.py
```

Tento skript vytvoří složku `vystupni_data`, pokud ještě neexistuje, a uloží do ní Excel soubory vytvořené z HTML tabulek.

---

### 3. Spuštění druhého skriptu

Po dokončení prvního skriptu spusťte:

```bash
python cisteni_upr.py
```

Tento skript zpracuje Excel soubory ve složce `vystupni_data`, vytvoří upravené soubory a finální soubor:

```text
vystupni_data/vse_komplet.xlsx
```

---

## Popis zpracování

### Zpracování HTML souborů

Skript `parceling1.py` načítá všechny soubory s příponou `.html` ze složky `vstupni_data`.

Pomocí knihovny `BeautifulSoup` najde všechny HTML tabulky `<table>`.  
Každou tabulku projde po řádcích `<tr>` a z buněk `<td>` nebo `<th>` získá čistý text.

Každá tabulka je následně převedena na `pandas DataFrame` a uložena do samostatného listu Excel souboru.

---

### Zpracování Excel souborů

Skript `cisteni_upr.py` prochází všechny `.xlsx` soubory ve složce `vystupni_data`.

Ignoruje soubory, které už začínají na:

```text
upraveno_
```

nebo:

```text
vse_komplet
```

Z vybraných listů kopíruje pouze konkrétní rozsahy řádků:

```python
"Table_3":  řádky 21 až 37
"Table_4":  řádky 7 až 10
"Table_6":  řádky 27 až 35
"Table_7":  řádky 7 až 29
"Table_8":  řádky 7 až 35
"Table_9":  řádky 7 až 20
"Table_10": řádky 7 až 37
```

Tyto řádky se zkopírují do nového listu `Komplet`.

Po zpracování se odstraní původní listy `Table_1` až `Table_21`.

---

## Výstupní soubory

Po spuštění obou skriptů vzniknou ve složce `vystupni_data` tyto typy souborů:

```text
soubor.xlsx
```

Excel soubor vytvořený z původního HTML souboru.

```text
upraveno_soubor.xlsx
```

Upravený Excel soubor obsahující pouze list `Komplet`.

```text
vse_komplet.xlsx
```

Finální soubor, ve kterém jsou spojeny všechny listy `Komplet` z upravených souborů.

---

## Doporučený pracovní postup

1. Vložte HTML soubory do složky `vstupni_data`.
2. Spusťte `parceling1.py`.
3. Zkontrolujte vytvořené Excel soubory ve složce `vystupni_data`.
4. Spusťte `cisteni_upr.py`.
5. Použijte finální soubor `vystupni_data/vse_komplet.xlsx`.

---

## Poznámky

- Skripty očekávají, že vstupní HTML soubory mají příponu `.html`.
- Výstupní Excel soubory se ukládají ve formátu `.xlsx`.
- Druhý skript pracuje pouze se soubory ve složce `vystupni_data`.
- Pokud list `Komplet` už v souboru existuje, skript jej odstraní a vytvoří znovu.
- Finální soubor `vse_komplet.xlsx` spojuje data vedle sebe po sloupcích.
