import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import sys
import numpy as np

import matplotlib
matplotlib.use('Agg')

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(script_dir)

ALLOWED_PARAMS = ["Opt rcv pwr", "Q factor", "Signal to noise ratio", "Fec ber"]

def natural_key(string_):
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', string_)]

def clean_parameter_name(raw_name):
    return raw_name.replace('-', ' ').capitalize()

def get_fixed_phases_statistics(df, filename, num_pressures):
    if 'Opt rcv pwr' not in df.columns or len(df) < 20:
        return pd.DataFrame(), None

    target_phases_count = num_pressures * 2
    signal = df['Opt rcv pwr'].rolling(window=21, center=True, min_periods=1).median()
    p10 = signal.quantile(0.1)
    p90 = signal.quantile(0.9)
    threshold = (p10 + p90) / 2
    
    is_pressure = signal < threshold
    df_temp = df.copy()
    df_temp['Is_Pressure'] = is_pressure
    df_temp['Phase_ID'] = (df_temp['Is_Pressure'] != df_temp['Is_Pressure'].shift()).cumsum()
    
    raw_phases = df_temp.groupby('Phase_ID').agg({
        'Time [s]': ['min', 'max', 'count'],
        'Q factor': 'median',
        'Opt rcv pwr': 'median',
        'Signal to noise ratio': 'median',
        'Fec ber': 'median',
        'Is_Pressure': 'first'
    })
    raw_phases.columns = ['Start', 'End', 'Count', 'Q_Med', 'Pwr_Med', 'SNR_Med', 'BER_Med', 'Is_Pressure']
    raw_phases = raw_phases[raw_phases['Count'] > 4].copy()
    
    phase_names = []
    p_idx, k_idx = 1, 1
    for _, row in raw_phases.iterrows():
        if row['Is_Pressure']:
            phase_names.append(f"Síla {p_idx}")
            p_idx += 1
        else:
            phase_names.append(f"Klid {k_idx}")
            k_idx += 1
            
    raw_phases['Fáze'] = phase_names
    raw_phases['Soubor'] = filename
    return raw_phases[['Soubor', 'Fáze', 'Start', 'End', 'Q_Med', 'Pwr_Med', 'SNR_Med', 'BER_Med']].head(target_phases_count), threshold

def process_file(input_path):
    pattern = re.compile(
        r"logical_interface=(?P<logical_interface>[^,]+),"
        r"pm_interval=(?P<interval>[^,]+),pm_profile=(?P<profile>\S+)\s+"
        r"[\w-]+:(?P<parameter>[^=]+)=(?P<value>[^\s]+)\s+(?P<timestamp>\d+)"
    )
    all_raw_data = []
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    d = match.groupdict()
                    clean_name = clean_parameter_name(d['parameter'])
                    if clean_name in ALLOWED_PARAMS:
                        d['timestamp'] = int(d['timestamp'])
                        d['parameter_clean'] = clean_name
                        all_raw_data.append(d)
    except Exception as e:
        print(f"Chyba při čtení souboru: {e}")
        return None

    if not all_raw_data: return None

    start_ts = all_raw_data[0]['timestamp']
    measurements, current_row, last_ts = [], {}, None
    for d in all_raw_data:
        ts = d['timestamp']
        col = d['parameter_clean']
        if (last_ts and (ts - last_ts) > 2*10**9) or (col in current_row):
            measurements.append(current_row)
            current_row = {}
        current_row[col] = d['value']
        current_row['Time [s]'] = round((ts - start_ts) / 10**9, 1)
        last_ts = ts
    if current_row: measurements.append(current_row)
    df = pd.DataFrame(measurements).apply(pd.to_numeric, errors='coerce')

    for col in ALLOWED_PARAMS:
        if col in df.columns and df[col].notna().sum() > 5:
            df[col] = df[col].rolling(window=11, center=True, min_periods=1).median().ffill().bfill()
    return df

def main():
    input_folder, output_folder = 'vstup', 'vystup'
    
    print(f"Pracovní složka: {script_dir}")
    print("-" * 30)
    print("1: Rameno (detekce fází Klid/Síla)")
    print("2: Ostatní (pouze celkové průměry a odchylky)")
    choice = input("Vyberte možnost (1 nebo 2): ")

    num_pressures = 0
    if choice == '1':
        try:
            val = input("Zadejte počet působení sily (kolikrát rameno působila na prvek), které má program najít: ")
            num_pressures = int(val)
        except ValueError:
            print("Neplatný vstup, použita výchozí hodnota 4.")
            num_pressures = 4
    
    if not os.path.exists(input_folder):
        print(f"\nCHYBA: Složka '{input_folder}' nebyla nalezena!")
        print(f"Ujistěte se, že ve složce:\n{script_dir}\nje vytvořena složka 'vstup' se soubory .perf")
        input("\nStiskněte Enter pro ukončení...")
        return

    if not os.path.exists(output_folder): os.makedirs(output_folder)
    
    all_dfs, all_stats, all_summaries_list = {}, [], []
    files = sorted([f for f in os.listdir(input_folder) if f.endswith(".perf")], key=natural_key)

    if not files:
        print(f"Ve složce '{input_folder}' nejsou žádné soubory .perf!")
        input("\nStiskněte Enter pro ukončení...")
        return

    for filename in files:
        base_name = os.path.splitext(filename)[0]
        df = process_file(os.path.join(input_folder, filename))
        if df is not None:
            all_dfs[base_name] = df
            
            with PdfPages(os.path.join(output_folder, f"{base_name}.pdf")) as pdf:
                for col in ALLOWED_PARAMS:
                    if col in df.columns and df[col].notna().any():
                        fig, ax = plt.subplots(figsize=(10, 6))
                        ax.plot(df['Time [s]'], df[col], color='black', linewidth=1.5)
                        ax.set_title(f"Měření: {base_name} - {col}", fontweight='bold')
                        ax.set_xlabel("Čas [s]"); ax.set_ylabel(col)
                        if "ber" in col.lower(): ax.set_yscale('log')
                        ax.grid(True, which="both", linestyle=':', alpha=0.4)
                        plt.tight_layout(); pdf.savefig(); plt.close()

            if choice == '1':
                df_stats, threshold = get_fixed_phases_statistics(df, base_name, num_pressures)
                print(f"Zpracovávám (Rameno): {base_name} (fází: {len(df_stats)})")
                if not df_stats.empty: 
                    all_stats.append(df_stats)
                df.to_csv(os.path.join(output_folder, f"{base_name}.csv"), 
                          sep=';', index=False, decimal=',', encoding='utf-8-sig')
            else:
                print(f"Zpracovávám (Ostatní): {base_name}")
                summary_dict = {'Soubor': base_name}
                indiv_summary_rows = []
                for col in ALLOWED_PARAMS:
                    if col in df.columns:
                        mean_val = df[col].mean()
                        std_val = df[col].std()
                        indiv_summary_rows.append({'Parametr': col, 'Celkový průměr': mean_val, 'Směrodatná odchylka': std_val})
                        summary_dict[f'{col} (Průměr)'] = mean_val
                        summary_dict[f'{col} (Odchylka)'] = std_val
                
                pd.DataFrame(indiv_summary_rows).to_csv(os.path.join(output_folder, f"{base_name}_prumer.csv"), 
                                                       sep=';', index=False, decimal=',', encoding='utf-8-sig')
                all_summaries_list.append(summary_dict)

    if choice == '1' and all_stats:
        pd.concat(all_stats).to_csv(os.path.join(output_folder, "souhrnne_statistiky.csv"), 
                                    sep=';', index=False, decimal=',', encoding='utf-8-sig')

    if choice == '2' and all_summaries_list:
        pd.DataFrame(all_summaries_list).to_csv(os.path.join(output_folder, "souhrn_vsech_prumeru.csv"), 
                                               sep=';', index=False, decimal=',', encoding='utf-8-sig')

    if all_dfs:
        with PdfPages(os.path.join(output_folder, "srovnani_vsech_mereni.pdf")) as pdf:
            for param in ALLOWED_PARAMS:
                plt.figure(figsize=(12, 7))
                for name, df_plot in all_dfs.items():
                    if param in df_plot.columns:
                        plt.plot(df_plot['Time [s]'], df_plot[param], label=name, alpha=0.7)
                plt.title(f"Srovnání: {param}", fontweight='bold')
                if "ber" in param.lower(): plt.yscale('log')
                plt.grid(True, which="both", linestyle=':', alpha=0.6)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='x-small')
                plt.tight_layout(); pdf.savefig(); plt.close()

    print("\n" + "="*30)
    print("HOTOVO! Všechny soubory jsou ve složce 'vystup'.")
    input("Stiskněte Enter pro ukončení programu...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nNEOČEKÁVANÁ CHYBA: {e}")
        input("\nStiskněte Enter pro ukončení...")
