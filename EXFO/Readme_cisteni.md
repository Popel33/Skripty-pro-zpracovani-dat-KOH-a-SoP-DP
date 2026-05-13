# Excel Data Cleaner & Merger

Python skript pro automatické zpracování většího množství Excel souborů (`.xlsx`), extrakci vybraných dat z několika listů, vytvoření nového souhrnného listu **Komplet** a následné sloučení všech upravených souborů do jednoho finálního Excel souboru.

---

# Funkce skriptu

Skript provádí několik kroků:

1. Projde všechny Excel soubory ve složce `vystupni_data`
2. Otevře každý soubor
3. Vytvoří nový list `Komplet`
4. Z vybraných listů (`Table_3`, `Table_4`, atd.) zkopíruje definované rozsahy řádků
5. Odstraní původní listy `Table_1` až `Table_21`
6. Uloží nový upravený soubor s prefixem `upraveno_`
7. Nakonec spojí všechny listy `Komplet` ze všech upravených souborů do jednoho výsledného souboru `vse_komplet.xlsx`

---

# Použité knihovny

```python
import os
from openpyxl import load_workbook, Workbook
import re
```

## Knihovny

| Knihovna   | Účel                           |
| ---------- | ------------------------------ |
| `os`       | práce se soubory a složkami    |
| `openpyxl` | čtení a zápis Excel souborů    |
| `re`       | přirozené řazení názvů souborů |

---

# Struktura projektu

```text
projekt/
│
├── cisteni_upr.py
├── vystupni_data/
│   ├── soubor1.xlsx
│   ├── soubor2.xlsx
│   └── ...
```

---

# Detailní popis fungování

# 1. Nastavení složky

```python
folder_path = "vystupni_data"
upravene_soubory = []
```

## Co se zde děje

* `folder_path`

  * určuje složku se vstupními Excel soubory
* `upravene_soubory`

  * seznam, kam se ukládají cesty k nově vytvořeným souborům

---

# 2. Procházení všech Excel souborů

```python
for filename in os.listdir(folder_path):
```

Skript projde všechny soubory ve složce.

---

# 3. Filtrace souborů

```python
if filename.endswith(".xlsx") and not filename.startswith("upraveno_") and not filename.startswith("vse_komplet"):
```

## Skript zpracuje pouze

✅ `.xlsx` soubory

## Skript ignoruje

❌ již upravené soubory (`upraveno_*`)
❌ finální sloučený soubor (`vse_komplet.xlsx`)

---

# 4. Otevření workbooku

```python
workbook = load_workbook(file_path)
```

Načte Excel soubor do paměti.

---

# 5. Odstranění starého listu `Komplet`

```python
if "Komplet" in workbook.sheetnames:
    del workbook["Komplet"]
```

Pokud již list existuje, smaže se.

Důvod:

* zabránění duplicitám
* vytvoření čistého nového listu

---

# 6. Vytvoření nového listu `Komplet`

```python
komplet_sheet = workbook.create_sheet("Komplet")
```

Vytvoří nový list, do kterého se budou kopírovat data.

---

# 7. Definice kopírovaných rozsahů

```python
ranges_to_copy = {
    "Table_3": (21, 37),
    "Table_4": (7, 10),
    "Table_6": (27, 35),
    "Table_7": (7, 29),
    "Table_8": (7, 35),
    "Table_9": (7, 20),
    "Table_10": (7, 37),
}
```

## Význam

Každý záznam říká:

```python
"název_listu": (první_řádek, poslední_řádek)
```

Například:

```python
"Table_3": (21, 37)
```

znamená:

➡ z listu `Table_3` se zkopírují řádky 21 až 37.

---

# 8. Kopírování dat

```python
for row in sheet.iter_rows(min_row=start_row, max_row=end_row, values_only=True):
    komplet_sheet.append(row)
```

## Co se děje

* iterace přes definované řádky
* čtení pouze hodnot buněk (`values_only=True`)
* přidání řádku do listu `Komplet`

---

# 9. Mazání původních listů

```python
for i in range(1, 22):
```

Skript odstraní:

```text
Table_1
Table_2
...
Table_21
```

## Důvod

Po vytvoření souhrnného listu již původní listy nejsou potřeba.

---

# 10. Uložení upraveného souboru

```python
upraveny_nazev = f"upraveno_{filename}"
```

Například:

```text
data.xlsx
↓
upraveno_data.xlsx
```

---

# 11. Přirozené řazení souborů

```python
def natural_key(string):
```

Tato funkce řeší správné číselné řazení.

## Bez této funkce

```text
soubor1
soubor10
soubor2
```

## S funkcí

```text
soubor1
soubor2
soubor10
```

---

# 12. Vytvoření finálního workbooku

```python
vystupni_workbook = Workbook()
```

Vytvoří nový Excel soubor pro výsledné spojení dat.

---

# 13. Sloučení všech listů `Komplet`

```python
for file_path in upravene_soubory:
```

Skript:

1. otevře každý upravený soubor
2. načte list `Komplet`
3. vloží jeho obsah do finální tabulky

---

# 14. Vkládání dat vedle sebe

```python
start_col += ws.max_column
```

Každý další soubor se vloží:

➡ do dalších sloupců
➡ ne pod předchozí data

## Výsledek

```text
Soubor1 | Soubor2 | Soubor3
```

---

# 15. Uložení finálního souboru

```python
vystupni_soubor = os.path.join(folder_path, "vse_komplet.xlsx")
```

Výsledkem je:

```text
vystupni_data/vse_komplet.xlsx
```

---

# Výstup skriptu

Po dokončení vzniknou:

## Upravené soubory

```text
upraveno_soubor1.xlsx
upraveno_soubor2.xlsx
```

## Finální sloučený soubor

```text
vse_komplet.xlsx
```

---

# Jak skript spustit

## 1. Instalace knihovny

```bash
pip install openpyxl
```

---

## 2. Spuštění skriptu

```bash
python cisteni_upr.py
```

---

# Požadavky

* Python 3.9+
* openpyxl

---

# Možná budoucí rozšíření

## Možné vylepšení

* automatické formátování buněk
* zachování stylů z Excelu
* export do CSV
* GUI aplikace
* paralelní zpracování
* logování chyb
* automatická kontrola existence listů
* konfigurace přes JSON/YAML

---

