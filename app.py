import streamlit as st
import pandas as pd
from openpyxl import load_workbook
from io import BytesIO

st.set_page_config(page_title="Generatore Listino Temu", layout="wide")
st.title("🛒 Generatore Listino Temu")

# =========================
# FUNZIONI DI SUPPORTO
# =========================

def clean_outgoods(code):
    if pd.isna(code):
        return ""
    return str(code).split("_")[0]

def formato_label(fmt, sku=""):
    try:
        fmt = int(fmt)
    except:
        return ""

    if 1 <= fmt <= 6:
        return f"{fmt}x1L"
    if sku.lower().find("tan") != -1:
        return f"Tanica da {fmt}L"
    if fmt == 4:
        return "Tanica 4L"
    if fmt == 20:
        return "Tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "Fusto 205L"
    return f"{fmt}L"

def bullet_formato(fmt, sku=""):
    try:
        fmt = int(fmt)
    except:
        return ""
    if 1 <= fmt <= 6:
        return f"confezione da {fmt}x1L"
    if sku.lower().find("tan") != -1:
        return f"Tanica da {fmt}L"
    if fmt == 4:
        return "Tanica 4L"
    if fmt == 20:
        return "Tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "Fusto 205L"
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
        formato_label(row.get("Formato (L)",""), sku=row.get("Sku","")),
        str(row.get("Utilizzo",""))
    ]
    return " ".join([p for p in parts if p])

# =========================
# UPLOAD FILE
# =========================

st.subheader("📤 Carica file input e template Temu")

listino_file = st.file_uploader("File listino (Excel)", type=["xlsx"])
template_file = st.file_uploader("Template Temu scaricato (Excel)", type=["xlsx"])

if listino_file and template_file:
    df_listino = pd.read_excel(listino_file)
    st.subheader("Anteprima file input")
    st.dataframe(df_listino.head())

    # =========================
    # APRI TEMPLATE CON openpyxl
    # =========================
    wb = load_workbook(template_file)
    ws = wb.active  # assumiamo che i dati siano nel primo foglio

    # =========================
    # TROVA COLONNE NEL TEMPLATE
    # =========================
    header = [cell.value for cell in ws[1]]
    col_map = {name: idx for idx, name in enumerate(header)}

    # =========================
    # AGGIUNGI DATI DAL LISTINO
    # =========================
    start_row = ws.max_row + 1

    for idx, row in df_listino.iterrows():
        r = start_row + idx
        # esempio mappatura minima, aggiungi altre colonne come vuoi
        ws.cell(row=r, column=col_map.get("Nome dell'Articolo",1)).value = nome_articolo(row)
        ws.cell(row=r, column=col_map.get("outGoodsSn",1)).value = clean_outgoods(row.get("Codice prodotto",""))
        ws.cell(row=r, column=col_map.get("outSkuSn",1)).value = row.get("Sku","")
        ws.cell(row=r, column=col_map.get("Aggiorna o aggiungi",1)).value = "Aggiorna/Aggiungi nuovo"
        ws.cell(row=r, column=col_map.get("Marca",1)).value = row.get("Marca","")
        ws.cell(row=r, column=col_map.get("Descrizione dell'articolo",1)).value = row.get("Descrizione","")
        ws.cell(row=r, column=col_map.get("Punto elenco",1)).value = "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti."
        ws.cell(row=r, column=col_map.get("Punto elenco_2",1)).value = row.get("Descrizione breve","")
        ws.cell(row=r, column=col_map.get("Punto elenco_3",1)).value = bullet_formato(row.get("Formato (L)",""), sku=row.get("Sku",""))
        ws.cell(row=r, column=col_map.get("Punto elenco_4",1)).value = "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione."
        # URL immagini
        for i in range(1,8):
            col_name = f"URL delle immagini dei dettagli"  # ripetuta
            if col_name in col_map:
                ws.cell(row=r, column=col_map[col_name]+(i-1)).value = row.get(f"Img {i}","")
        # SKU immagine
        ws.cell(row=r, column=col_map.get("URL immagini SKU",1)).value = row.get("Img 1","")
        # Capacità e quantità
        cap, qty = capacita_quantita(row.get("Formato (L)",""))
        ws.cell(row=r, column=col_map.get("Capacità",1)).value = cap
        ws.cell(row=r, column=col_map.get("Quantità",1)).value = qty
        # Prezzi
        ws.cell(row=r, column=col_map.get("Prezzo base - EUR",1)).value = round((row.get("Prezzo Marketplace",0)/1.22)*0.85,2)
        ws.cell(row=r, column=col_map.get("Prezzo di listino - EUR",1)).value = row.get("Prezzo Marketplace",0)
        # Peso pacco
        ws.cell(row=r, column=col_map.get("Peso pacco - g",1)).value = int(row.get("Formato (L)",1)*1000)
        # Produttore
        ws.cell(row=r, column=col_map.get("Produttore",1)).value = produttore(row.get("Marca",""))

    # =========================
    # SALVA FILE NEL BUFFER
    # =========================
    output = BytesIO()
    wb.save(output)
    st.success("✅ File Temu aggiornato pronto per upload!")
    st.download_button(
        "⬇️ Scarica file Temu pronto",
        data=output.getvalue(),
        file_name="listino_temu_pronto.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
