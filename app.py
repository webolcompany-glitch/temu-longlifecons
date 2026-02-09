import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO

st.set_page_config(page_title="Generatore Listino Temu", layout="wide")
st.title("🛒 Generatore Listino Temu - Versione Finale")

# ---------------------
# FUNZIONI DI SUPPORTO
# ---------------------

def clean_outgoods(code):
    if pd.isna(code):
        return ""
    return str(code).split("_")[0]

def formato_label(fmt, sku):
    try:
        fmt = int(fmt)
    except:
        return ""
    # gestione tan special
    if isinstance(sku, str) and "tan" in sku.lower():
        return f"Tanica da {fmt}L"
    if 1 <= fmt <= 6:
        return f"{fmt}x1L"
    if fmt == 20:
        return "Tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "Fusto da 205L"
    return f"{fmt}L"

def bullet_formato(fmt, sku):
    try:
        fmt = int(fmt)
    except:
        return ""
    if isinstance(sku, str) and "tan" in sku.lower():
        return f"Tanica da {fmt}L"
    if 1 <= fmt <= 6:
        return f"confezione da {fmt}x1L"
    if fmt == 20:
        return "Tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "Fusto da 205L"
    return f"{fmt}L"

def capacita_quantita(fmt):
    try:
        fmt = int(fmt)
    except:
        return ("", "")
    if 1 <= fmt <= 6:
        return ("1", str(fmt))
    return (str(fmt), "1")

def produttore(marca):
    if str(marca).upper().strip() == "TAMOIL":
        return "TAMOIL ITALIA S.P.A."
    return "Long life consulting s.r.l."

def nome_articolo(row):
    parts = [
        str(row.get("Sottocategoria","")),
        str(row.get("Viscosità","")),
        str(row.get("Marca","")),
        str(row.get("ACEA","")),
        formato_label(row.get("Formato (L)"), row.get("Sku")),
        str(row.get("Utilizzo",""))
    ]
    return " ".join([p for p in parts if p])

# ---------------------
# CARICA FILE INPUT
# ---------------------

input_file = st.file_uploader("📤 Carica il file Excel di input", type=["xlsx"])
template_file = st.file_uploader("📤 Carica il template Temu originale", type=["xlsx"])

if input_file and template_file:
    df_input = pd.read_excel(input_file)
    st.subheader("Anteprima file input")
    st.dataframe(df_input.head())

    # Carica template Temu
    wb_template = load_workbook(template_file)
    ws = wb_template["Template"]

    # Lista intestazioni template
    headers = [cell.value for cell in ws[1]]

    # ---------------------
    # SCRITTURA DEI DATI
    # ---------------------
    for i, row in df_input.iterrows():
        r = i + 2  # start from row 2 in Excel
        for j, col in enumerate(headers):
            val = ""
            if col == "Nome dell'Articolo":
                val = nome_articolo(row)
            elif col == "outGoodsSn":
                val = clean_outgoods(row.get("Codice prodotto",""))
            elif col == "outSkuSn":
                val = row.get("Sku","")
            elif col == "Aggiorna o aggiungi":
                val = "Aggiorna/Aggiungi nuovo"
            elif col == "Marca":
                val = row.get("Marca","")
            elif col == "Descrizione dell'articolo":
                val = row.get("Descrizione","")
            elif col == "Punto elenco":
                val = "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici."
            elif col == "Punto elenco 2":
                val = row.get("Descrizione breve","")
            elif col == "Punto elenco 3":
                val = bullet_formato(row.get("Formato (L)"), row.get("Sku"))
            elif col == "Punto elenco 4":
                val = "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione."
            elif col.startswith("URL delle immagini dei dettagli"):
                img_idx = int(col.split(" ")[-1])
                val = row.get(f"Img {img_idx}", "")
            elif col == "Tema della variante":
                val = "Capacità × Quantità"
            elif col == "Capacità":
                cap, _ = capacita_quantita(row.get("Formato (L)"))
                val = cap
            elif col == "Quantità":
                _, qty = capacita_quantita(row.get("Formato (L)"))
                val = qty
            elif col == "URL delle immagini SKU":
                val = row.get("Img 1", "")
            elif col == "Prezzo base - EUR":
                pm = row.get("Prezzo Marketplace")
                if pm:
                    val = round((pm / 1.22) * 0.85,2)
            elif col == "Prezzo di listino - EUR":
                val = row.get("Prezzo Marketplace","")
            elif col == "Peso pacco - g":
                fmt = row.get("Formato (L)")
                if fmt:
                    val = int(fmt*1000)
            elif col == "Modello di spedizione":
                val = "Free"
            elif col == "Paese/Regione di origine":
                val = "Italy"
            elif col == "Produttore":
                val = produttore(row.get("Marca",""))
            elif col == "Persona responsabile per l'UE":
                val = "LONG LIFE CONSULTING S.R.L."
            # Scrive solo se valore non vuoto
            if val != "":
                ws.cell(row=r, column=j+1, value=val)

    # ---------------------
    # SALVATAGGIO FILE
    # ---------------------
    buffer = BytesIO()
    wb_template.save(buffer)
    st.success("✅ File Temu generato correttamente")
    st.download_button(
        "⬇️ Scarica file Temu pronto per upload",
        data=buffer.getvalue(),
        file_name="listino_temu_pronto.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
