import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re
from scipy.signal import savgol_filter
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.ticker as ticker

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, 'vstupSOP')
OUTPUT_DIR_PDF = os.path.join(SCRIPT_DIR, 'vystupSOP')

if not os.path.exists(OUTPUT_DIR_PDF):
    os.makedirs(OUTPUT_DIR_PDF)

def extract_number(filename):
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 999

def segment_signal_robust(bal_signal, fs):
    win = int(fs) if int(fs) % 2 != 0 else int(fs) + 1
    bal_smooth = savgol_filter(bal_signal, win, 2)
    
    noise_sample = bal_smooth[int(0.5*fs):int(2.5*fs)]
    base_median = np.median(noise_sample)
    base_std = np.std(noise_sample)
    
    diff = np.abs(bal_smooth - base_median)
    trigger_threshold = max(10 * base_std, 0.01)
    trigger_indices = np.where(diff > trigger_threshold)[0]
    
    if len(trigger_indices) > 0:
        first_trigger_idx = trigger_indices[0]
        end_ref = max(int(3 * fs), first_trigger_idx - int(2 * fs))
        end_ref = min(end_ref, int(30 * fs))
    else:
        end_ref = int(10 * fs)

    start_ref = int(1 * fs)
    ref_klid = np.median(bal_smooth[start_ref:end_ref])
    
    b_min, b_max = np.min(bal_smooth), np.max(bal_smooth)
    threshold = (b_min + b_max) / 2
    for _ in range(10):
        low_vals = bal_smooth[bal_smooth <= threshold]
        high_vals = bal_smooth[bal_smooth > threshold]
        if len(low_vals) == 0 or len(high_vals) == 0: break
        threshold = (np.mean(low_vals) + np.mean(high_vals)) / 2

    m_below = np.mean(bal_smooth[bal_smooth <= threshold]) if len(bal_smooth[bal_smooth <= threshold]) > 0 else ref_klid
    m_above = np.mean(bal_smooth[bal_smooth > threshold]) if len(bal_smooth[bal_smooth > threshold]) > 0 else ref_klid
    
    if abs(m_below - ref_klid) > abs(m_above - ref_klid):
        mask = (bal_smooth < threshold).astype(int)
    else:
        mask = (bal_smooth > threshold).astype(int)
    
    kernel = int(fs * 2)
    mask_smooth = np.convolve(mask, np.ones(kernel)/kernel, mode='same')
    mask = (mask_smooth > 0.5).astype(int)
    
    changes = np.diff(mask)
    starts = np.where(changes == 1)[0]
    ends = np.where(changes == -1)[0]
    
    if len(starts) > 0 and len(ends) > 0:
        if ends[0] < starts[0]: ends = ends[1:]
    min_len = min(len(starts), len(ends))
    starts, ends = starts[:min_len], ends[:min_len]
    
    phases = []
    if len(starts) > 0:
        phases.append({'type': 'Klid', 'start': int(1*fs), 'end': starts[0] - int(0.5*fs)})
    
    for i in range(len(starts)):
        s, e = starts[i], ends[i]
        if (e - s) < 3 * fs: continue
        margin = int((e - s) * 0.15) 
        phases.append({'type': 'Stisk', 'start': s + margin, 'end': e - margin})
        if i < len(starts) - 1:
            k_s, k_e = e, starts[i+1]
            if (k_e - k_s) > fs * 1:
                k_m = int((k_e - k_s) * 0.15)
                phases.append({'type': 'Klid', 'start': k_s + k_m, 'end': k_e - k_m})
    return phases

def process_file(file_path, filename, mode):
    mid = filename.split('-')[0]
    try:
        with h5py.File(file_path, 'r') as f:
            s0_raw = f['S0'][:]
            v_idx = np.where(s0_raw > 0)[0]
            if len(v_idx) == 0: return None
            lv = v_idx[-1]
            s0, s1, s2, s3 = s0_raw[:lv], f['S1'][:lv], f['S2'][:lv], f['S3'][:lv]
            bal = f['Bal'][:lv]
            fs = float(filename.replace('.hdf5','').split('_')[-1])
    except: return None

    with np.errstate(divide='ignore', invalid='ignore'):
        s1_n, s2_n, s3_n = np.where(s0!=0, s1/s0, 0), np.where(s0!=0, s2/s0, 0), np.where(s0!=0, s3/s0, 0)
    
    s1_s = savgol_filter(s1_n, 51, 3)
    s2_s = savgol_filter(s2_n, 51, 3)
    s3_s = savgol_filter(s3_n, 51, 3)
    dop = np.sqrt(s1_s**2 + s2_s**2 + s3_s**2)
    bal_s = savgol_filter(bal, 501, 3)
    
    t = np.arange(len(s0)) / fs
    step = 20

    df_plot = pd.DataFrame({
        'Cas_s': t[::step], 'S1': s1_s[::step], 'S2': s2_s[::step],
        'S3': s3_s[::step], 'DOP': dop[::step], 'BAL_V': bal_s[::step]
    })
    df_plot.to_csv(os.path.join(OUTPUT_DIR_PDF, f"{mid}_data.csv"), sep=';', index=False, encoding='utf-8-sig')

    if mode == '1': 
        phases = segment_signal_robust(bal, fs)
        
        pdf_p = os.path.join(OUTPUT_DIR_PDF, f"{mid}.pdf")
        with PdfPages(pdf_p) as pdf:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
            for ax in [ax1, ax2, ax3]:
                ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
                ax.grid(True, alpha=0.3)
                for p in phases:
                    c = 'green' if p['type'] == 'Klid' else 'red'
                    ax.axvspan(p['start']/fs, p['end']/fs, color=c, alpha=0.15)
            ax1.plot(t[::step], s1_s[::step], label='S1'); ax1.plot(t[::step], s2_s[::step], label='S2'); ax1.plot(t[::step], s3_s[::step], label='S3')
            ax1.set_title(f"ID: {mid} | Fází: {len(phases)} (RAMENO)"); ax1.legend(loc='upper right')
            ax2.plot(t[::step], dop[::step], color='black', label='DOP'); ax2.legend(loc='upper right')
            ax3.plot(t[::step], bal_s[::step], color='brown', label='Bal [V]'); ax3.legend(loc='upper right')
            plt.tight_layout(); pdf.savefig(fig); plt.close(fig)

        meta = {'ID': mid, 'Pocet_Stisku': sum(1 for p in phases if p['type'] == 'Stisk')}
        d_all, d_bal, d_dop, d_vec = {**meta}, {**meta}, {**meta}, {**meta}
        kc, sc = 1, 1
        for p in phases:
            lbl = f"{p['type']}{kc if p['type'] == 'Klid' else sc}"
            v1, v2, v3 = np.median(s1_s[p['start']:p['end']]), np.median(s2_s[p['start']:p['end']]), np.median(s3_s[p['start']:p['end']])
            vdop, vbal = np.median(dop[p['start']:p['end']]), np.median(bal_s[p['start']:p['end']])
            d_bal[f"{lbl}_Bal"] = vbal
            d_dop[f"{lbl}_DOP"] = vdop
            d_vec.update({f"{lbl}_S1": v1, f"{lbl}_S2": v2, f"{lbl}_S3": v3})
            d_all.update({f"{lbl}_S1": v1, f"{lbl}_S2": v2, f"{lbl}_S3": v3, f"{lbl}_DOP": vdop, f"{lbl}_Bal": vbal})
            if p['type'] == 'Klid': kc += 1
            else: sc += 1
        return d_all, d_bal, d_dop, d_vec

    else: 
        pdf_p = os.path.join(OUTPUT_DIR_PDF, f"{mid}.pdf")
        with PdfPages(pdf_p) as pdf:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
            for ax in [ax1, ax2, ax3]:
                ax.xaxis.set_major_locator(ticker.MultipleLocator(10)); ax.grid(True, alpha=0.3)
            ax1.plot(t[::step], s1_s[::step], label='S1'); ax1.plot(t[::step], s2_s[::step], label='S2'); ax1.plot(t[::step], s3_s[::step], label='S3')
            ax1.set_title(f"ID: {mid} (OSTATNÍ)"); ax1.legend(loc='upper right')
            ax2.plot(t[::step], dop[::step], color='black', label='DOP'); ax2.legend(loc='upper right')
            ax3.plot(t[::step], bal_s[::step], color='brown', label='Bal [V]'); ax3.legend(loc='upper right')
            plt.tight_layout(); pdf.savefig(fig); plt.close(fig)

        stats = {
            'ID': mid,
            'S1_Prumer': np.mean(s1_s), 'S1_Odchylka': np.std(s1_s),
            'S2_Prumer': np.mean(s2_s), 'S2_Odchylka': np.std(s2_s),
            'S3_Prumer': np.mean(s3_s), 'S3_Odchylka': np.std(s3_s),
            'DOP_Prumer': np.mean(dop), 'DOP_Odchylka': np.std(dop),
            'BAL_Prumer': np.mean(bal_s), 'BAL_Odchylka': np.std(bal_s)
        }
        return stats

if __name__ == "__main__":
    if not os.path.exists(INPUT_DIR):
        print(f"CHYBA: Složka '{INPUT_DIR}' nenalezena!")
    else:
        print("VYBERTE REŽIM ZPRACOVÁNÍ:")
        print("1 - Rameno (kompletní analýza, hledání výraznějších změn během měření)")
        print("2 - Ostatní (pouze grafy a celkové průměry)")
        volba = input("Zadejte volbu (1 nebo 2): ").strip()
        
        if volba not in ['1', '2']:
            print("Neplatná volba. Ukončuji program.")
        else:
            files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.hdf5')], key=extract_number)
            results = []
            print(f"\n--- START ANALÝZY (Režim: {'Rameno' if volba=='1' else 'Ostatní'}) ---")
            
            for f in files:
                res = process_file(os.path.join(INPUT_DIR, f), f, volba)
                if res:
                    results.append(res)
                    print(f"  {f.split('-')[0]}: OK")
            
            if results:
                cfg = {'sep': ';', 'index': False, 'encoding': 'utf-8-sig'}
                if volba == '1':
                    pd.DataFrame([r[0] for r in results]).to_csv(os.path.join(SCRIPT_DIR, 'VYSLEDKY_MASTER.csv'), **cfg)
                    pd.DataFrame([r[1] for r in results]).to_csv(os.path.join(SCRIPT_DIR, 'VYSLEDKY_BAL.csv'), **cfg)
                    pd.DataFrame([r[2] for r in results]).to_csv(os.path.join(SCRIPT_DIR, 'VYSLEDKY_DOP.csv'), **cfg)
                    pd.DataFrame([r[3] for r in results]).to_csv(os.path.join(SCRIPT_DIR, 'VYSLEDKY_VEKTORY.csv'), **cfg)
                else:
                    pd.DataFrame(results).to_csv(os.path.join(SCRIPT_DIR, 'Prumery_komplet.csv'), **cfg)
                
                print(f"\nHotovo. Výsledky uloženy ve složce: {SCRIPT_DIR}")
