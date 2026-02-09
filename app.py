import streamlit as st
import pandas as pd
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
    if "tan" in sku.lower():
        return f"Tanica da {fmt}L"
    if 1 <= fmt <= 6:
        return f"{fmt}x1L"
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
    if "tan" in sku.lower():
        return f"Tanica da {fmt}L"
    if 1 <= fmt <= 6:
        return f"confezione da {fmt}x1L"
    if fmt == 4:
        return "Tanica 4L"
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

def tipo_da_utilizzo(utilizzo):
    if pd.isna(utilizzo):
        return ""
    u = str(utilizzo).lower()
    motore_keys = [
        "per auto", "per motori", "per macchine agricole",
        "per la lubrificazione dei motori a due tempi",
        "per motori a due tempi come moto da cross e scooters",
        "per motori a due tempi raffreddati ad aria",
        "per motori fuoribordo a 2 tempi"
    ]
    cambi_keys = [
        "per cambi, differenziali e trasmissioni",
        "per trasmissioni e differenziali",
        "per cambi e differenziali"
    ]
    for k in motore_keys:
        if u.startswith(k):
            return "Motore"
    for k in cambi_keys:
        if u.startswith(k):
            return "Per trasmissioni e differenziali"
    return ""

def nome_articolo(row):
    parts = [
        row.get("Sottocategoria", ""),
        row.get("Viscosità", ""),
        row.get("Marca", ""),
        row.get("ACEA", ""),
        formato_label(row.get("Formato (L)", ""), row.get("Sku", "")),
        row.get("Utilizzo", "")
    ]
    return " ".join([str(p) for p in parts if p])

# =========================
# UPLOAD FILE
# =========================

file = st.file_uploader("📤 Carica il file Excel di input", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.subheader("Anteprima file input")
    st.dataframe(df.head())

    output_rows = []

    for _, row in df.iterrows():
        cap, qty = capacita_quantita(row.get("Formato (L)", ""))

        output_rows.append({
            "Categoria": 20416,
            "Nome della categoria": "",
            "Tipo di articolo": "",
            "Nome dell'Articolo": nome_articolo(row),
            "outGoodsSn": clean_outgoods(row.get("Codice prodotto", "")),
            "outSkuSn": row.get("Sku", ""),
            "Aggiorna o aggiungi": "Aggiorna/Aggiungi nuovo",
            "Marca": row.get("Marca", ""),
            "Marchio": "",
            "Descrizione dell'articolo": row.get("Descrizione", ""),
            "Punto elenco 1": "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici.",
            "Punto elenco 2": row.get("Descrizione breve", ""),
            "Punto elenco 3": bullet_formato(row.get("Formato (L)", ""), row.get("Sku", "")),
            "Punto elenco 4": "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione.",
            # URL immagini dettagli separati
            **{f"URL delle immagini dei dettagli {i}": row.get(f"Img {i}", "") for i in range(1, 8)},
            "Tema della variante": "Capacità × Quantità",
            "Capacità": cap,
            "Quantità": qty,
            "URL immagini SKU": row.get("Img 1", ""),
            "Quantità stock": 10,
            "Prezzo base - EUR": round((row.get("Prezzo Marketplace", 0) / 1.22) * 0.85, 2),
            "Prezzo di listino - EUR": row.get("Prezzo Marketplace", 0),
            "Peso pacco - g": int(row.get("Formato (L)", 0) * 1000),
            "Lunghezza - cm": 25,
            "Larghezza - cm": 25,
            "Altezza - cm": 25,
            "Modello di spedizione": "Free",
            "Paese/Regione di origine": "Italy",
            "Produttore": produttore(row.get("Marca", "")),
            "Persona responsabile per l'UE": "LONG LIFE CONSULTING S.R.L."
        })

    df_out = pd.DataFrame(output_rows)

    # =========================
    # EXPORT EXCEL
    # =========================

    buffer = BytesIO()
    df_out.to_excel(buffer, index=False)
    buffer.seek(0)

    st.success("✅ File Temu generato correttamente")
    st.download_button(
        "⬇️ Scarica file Temu",
        data=buffer.getvalue(),
        file_name="listino_temu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
