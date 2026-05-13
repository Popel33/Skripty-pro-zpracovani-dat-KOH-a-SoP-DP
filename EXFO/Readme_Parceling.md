# HTML Table Extractor to Excel

Tento Python skript slouží k automatickému zpracování HTML souborů, ze kterých vyhledá všechny tabulky a uloží je do samostatných Excel souborů ve formátu `.xlsx`.

Skript projde všechny soubory s příponou `.html` ve vstupní složce, najde v nich HTML tabulky a každou tabulku uloží jako samostatný list v odpovídajícím Excel souboru.

---

# Funkce skriptu

Skript provádí tyto hlavní kroky:

1. Načte HTML soubor
2. Pomocí knihovny `BeautifulSoup` vyhledá všechny HTML tabulky
3. Z každé tabulky načte řádky a buňky
4. Převede data do `pandas DataFrame`
5. Každou tabulku uloží do Excelu
6. Každá HTML tabulka bude v Excelu na samostatném listu
7. Výsledné `.xlsx` soubory uloží do složky `vystupni_data`

---

# Struktura projektu

```text
projekt/
│
├── parceling1.py
│
├── vstupni_data/
│   ├── soubor1.html
│   ├── soubor2.html
│   └── ...
│
└── vystupni_data/
    ├── soubor1.xlsx
    ├── soubor2.xlsx
    └── ...
```

---

# Instalace

Nejprve nainstalujte potřebné knihovny:

```bash
pip install beautifulsoup4 pandas openpyxl
```

Použité knihovny:

* `os`
* `BeautifulSoup`
* `pandas`
* `openpyxl`

---

# Jak skript funguje

## 1. Načtení HTML souboru

Skript otevře HTML soubor:

```python
with open(file_path, "r", encoding="utf-8") as file:
```

---

## 2. Parsování HTML

HTML obsah je načten pomocí `BeautifulSoup`:

```python
soup = BeautifulSoup(file, "html.parser")
```

---

## 3. Vyhledání tabulek

Skript najde všechny HTML tabulky:

```python
tables = soup.find_all("table")
```

---

## 4. Načtení řádků a buněk

Každá tabulka je procházena po řádcích:

```python
for row in table.find_all("tr"):
```

Načítají se všechny buňky `<td>` i `<th>`:

```python
cells = row.find_all(["td", "th"])
```

Text z buněk se očistí:

```python
cell.get_text(strip=True)
```

---

## 5. Převod do DataFrame

Data jsou převedena do `pandas DataFrame`:

```python
df = pd.DataFrame(rows)
```

---

## 6. Uložení do Excelu

Každá tabulka se uloží jako samostatný list:

```python
table.to_excel(
    writer,
    index=False,
    header=False,
    sheet_name=f"Table_{i+1}"
)
```

Příklad názvů listů:

* `Table_1`
* `Table_2`
* `Table_3`

---

# Automatické zpracování všech HTML souborů

Skript projde všechny soubory ve složce:

```python
for filename in os.listdir(input_folder):
```

Zpracovávají se pouze `.html` soubory:

```python
if filename.endswith(".html"):
```

---

# Nastavení vstupní a výstupní složky

```python
input_dir = "vstupni_data"
output_dir = "vystupni_data"
```

---

# Spuštění skriptu

1. Vložte HTML soubory do složky:

```text
vstupni_data
```

2. Spusťte skript:

```bash
python parceling1.py
```

3. Výsledné Excel soubory se uloží do:

```text
vystupni_data
```

---

# Příklad

Vstup:

```text
vstupni_data/objednavky.html
```

Výstup:

```text
vystupni_data/objednavky.xlsx
```

Pokud HTML obsahuje více tabulek, budou v Excelu na samostatných listech.

---

# Omezení skriptu

Aktuální verze:

* podporuje pouze `.html`
* neřeší `rowspan` a `colspan`
* nepřidává vlastní názvy sloupců
* neformátuje Excel soubory
* neprovádí validaci HTML

---

# Možná budoucí vylepšení

* podpora `.htm`
* automatické názvy listů
* formátování Excelu
* podpora sloučených buněk
* logování průběhu
* statistiky počtu tabulek
* argumenty příkazové řádky

---

# Shrnutí

`parceling1.py` je jednoduchý nástroj pro převod HTML tabulek do Excel formátu.

Je vhodný pro hromadné zpracování HTML souborů a export tabulkových dat do `.xlsx`.
