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

def formato_label(fmt):
    try:
        fmt = int(fmt)
    except:
        return ""

    if 1 <= fmt <= 6:
        return f"{fmt}x1L"
    if fmt == 4:
        return "tanica 4L"
    if fmt == 20:
        return "tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "fusto 205L"
    return f"{fmt}L"

def bullet_formato(fmt):
    try:
        fmt = int(fmt)
    except:
        return ""

    if 1 <= fmt <= 6:
        return f"confezione da {fmt}x1L"
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
        return ("", "")
    u = utilizzo.lower()

    motore_keys = [
        "per auto", "per motori", "per macchine agricole",
        "due tempi", "2 tempi", "motori a due tempi",
        "fuoribordo", "raffreddati ad aria"
    ]

    cambi_keys = [
        "per cambi, differenziali e trasmissioni",
        "per trasmissioni e differenziali",
        "per cambi e differenziali"
    ]

    for k in motore_keys:
        if u.startswith(k):
            return ("Motore", utilizzo.replace(k, "").strip())

    for k in cambi_keys:
        if u.startswith(k):
            return ("Per trasmissioni e differenziali", utilizzo.replace(k, "").strip())

    return ("", utilizzo)

def nome_articolo(row):
    tipo, utilizzo_residuo = tipo_da_utilizzo(row["Utilizzo"])
    parts = [
        "Olio",
        tipo,
        row["Viscosità"],
        row["Marca"],
        row["Marca"],
        row["ACEA"],
        formato_label(row["Formato (L)"]),
    ]
    if utilizzo_residuo:
        parts.append(utilizzo_residuo)
    return " ".join([str(p) for p in parts if p])

# =========================
# UPLOAD FILE
# =========================

file = st.file_uploader("📤 Carica il file Excel di input", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.subheader("Anteprima file input")
    st.dataframe(df.head())

    # =========================
    # CREAZIONE FILE TEMU
    # =========================

    output_rows = []

    for _, row in df.iterrows():
        cap, qty = capacita_quantita(row["Formato (L)"])

        output_rows.append({
            "Categoria": 20416,
            "Nome della categoria": "",
            "Tipo di articolo": "",
            "Nome dell'Articolo": nome_articolo(row),
            "outGoodsSn": clean_outgoods(row["Codice prodotto"]),
            "outSkuSn": row["Sku"],
            "Aggiorna o aggiungi": "Aggiorna/Aggiungi nuovo",
            "Marca": row["Marca"],
            "Marchio": "",
            "Descrizione dell'articolo": row["Descrizione"],
            "Punto elenco 1": "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici.",
            "Punto elenco 2": row["Descrizione breve"],
            "Punto elenco 3": bullet_formato(row["Formato (L)"]),
            "Punto elenco 4": "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione.",
            "URL Img 1": row["Img 1"],
            "URL Img 2": row["Img 2"],
            "URL Img 3": row["Img 3"],
            "URL Img 4": row["Img 4"],
            "URL Img 5": row["Img 5"],
            "URL Img 6": row["Img 6"],
            "URL Img 7": row["Img 7"],
            "Tema della variante": "Capacità × Quantità",
            "Capacità": cap,
            "Quantità variante": qty,
            "URL immagini SKU": row["Img 1"],
            "Quantità stock": 10,
            "Prezzo base - EUR": round((row["Prezzo Marketplace"] / 1.22) * 0.85, 2),
            "Prezzo di listino - EUR": row["Prezzo Marketplace"],
            "Peso pacco - g": int(row["Formato (L)"] * 1000),
            "Lunghezza - cm": 25,
            "Larghezza - cm": 25,
            "Altezza - cm": 25,
            "Modello di spedizione": "Free",
            "Paese/Regione di origine": "Italy",
            "Produttore": produttore(row["Marca"]),
            "Persona responsabile per l'UE": "LONG LIFE CONSULTING S.R.L."
        })

    df_out = pd.DataFrame(output_rows)

    # =========================
    # EXPORT EXCEL CON DOPPIO HEADER
    # =========================

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Temu")
        writer.sheets["Temu"] = worksheet

        header_row_1 = [
            "Identità dell'articolo", "", "", "Descrizione dell'articolo", "", "",
            "Proprietà di vendita", "", "", "", "", "", "",
            "Variazioni", "", "", "", "", "",
            "Offerta", "",
            "Titoli di studio"
        ]

        worksheet.write_row(0, 0, header_row_1)
        df_out.to_excel(writer, sheet_name="Temu", startrow=1, index=False)

    st.success("✅ File Temu generato correttamente")
    st.download_button(
        "⬇️ Scarica file Temu",
        data=buffer.getvalue(),
        file_name="listino_temu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

