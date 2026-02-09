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
        return "Tanica 4L"
    if fmt == 20:
        return "Tanica 20L"
    if fmt == 55:
        return "Fustino 55L"
    if fmt == 205:
        return "Fusto 205L"
    return f"{fmt}L"

def bullet_formato(fmt, sku):
    try:
        fmt = int(fmt)
    except:
        return ""
    if "tan" in str(sku).lower():
        return f"Tanica da {fmt}L"
    if 1 <= fmt <= 6:
        return f"confezione da {fmt}x1L"
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
        str(row.get("Sottocategoria", "")),
        str(row.get("Viscosità", "")),
        str(row.get("Marca", "")),
        str(row.get("ACEA", "")),
        formato_label(row.get("Formato (L)", "")),
        str(row.get("Utilizzo", ""))
    ]
    return " ".join([p for p in parts if p])

# =========================
# UPLOAD FILE
# =========================

file = st.file_uploader("📤 Carica il file Excel di input", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    st.subheader("Anteprima file input")
    st.dataframe(df.head())

    # =========================
    # DEFINIZIONE TUTTE LE COLONNE TEMU
    # =========================

    temu_columns = [
        "Categoria","Nome della categoria","Tipo di articolo","Tecnica di lavorazione personalizzata","Tecnica primaria",
        "Tecnica secondaria","Tecnica secondaria","Nome dell'Articolo","outGoodsSn","outSkuSn","Aggiorna o aggiungi",
        "ID articoli","ID SKU","Marca","Marchio","Descrizione dell'articolo",
        "Punto elenco 1","Punto elenco 2","Punto elenco 3","Punto elenco 4","Punto elenco 5","Punto elenco 6",
        "URL Img 1","URL Img 2","URL Img 3","URL Img 4","URL Img 5","URL Img 6","URL Img 7",
        "URL Img 8","URL Img 9","URL Img 10","URL Img 11","URL Img 12","URL Img 13","URL Img 14","URL Img 15",
        "URL Img 16","URL Img 17","URL Img 18","URL Img 19","URL Img 20","URL Img 21","URL Img 22","URL Img 23",
        "URL Img 24","URL Img 25","URL Img 26","URL Img 27","URL Img 28","URL Img 29","URL Img 30","URL Img 31",
        "URL Img 32","URL Img 33","URL Img 34","URL Img 35","URL Img 36","URL Img 37","URL Img 38","URL Img 39",
        "URL Img 40","URL Img 41","URL Img 42","URL Img 43","URL Img 44","URL Img 45","URL Img 46","URL Img 47",
        "URL Img 48","URL Img 49","URL Img 50","URL del video dei dettagli",
        "124 - Tipo di contenitore","901 - Grado di viscosità SAE","Tema della variante","Colore","Dimensioni",
        "Stile","Materiale","Sapori","Persone applicabili","Capacità","Composizione","Peso","Elementi","Quantità",
        "Modello","Lunghezza dei capelli","URL immagini SKU 1","URL immagini SKU 2","URL immagini SKU 3","URL immagini SKU 4",
        "URL immagini SKU 5","URL immagini SKU 6","URL immagini SKU 7","URL immagini SKU 8","URL immagini SKU 9","URL immagini SKU 10",
        "Quantità stock","Prezzo base - EUR","Link di riferimento","Prezzo di listino - EUR","Non disponibile per il prezzo di listino",
        "Peso pacco - g","Lunghezza - cm","Larghezza - cm","Altezza - cm","Tipo SKU","In confezione singola",
        "Quantità confezioni totale","Unità di imballaggio","Quantità totale di articoli","Unità articolo","Contenuto netto",
        "Contenuto netto totale","Unità di contenuto netto","Tipo di ID articolo esterno","ID Articolo Esterno",
        "Modello di spedizione","Tempo di trattamento","Canale di evasione","Codice fiscale dell'articolo (ITC)",
        "Paese/Regione di origine","Provincia di origine","Informazioni sulla confezione SKU (con etichetta visibile) 1",
        "Informazioni sulla confezione SKU (con etichetta visibile) 2","Informazioni sulla confezione SKU (con etichetta visibile) 3",
        "Etichetta di origine e informazioni sul produttore",
        "Degli articoli con questo ID articolo sono stati immessi sul mercato dell'Unione Europea (o dell'Irlanda del Nord) dopo il 13 dicembre 2024?",
        "Identificazione dell'articolo","Produttore","Persona responsabile per l'UE."
    ]

    # =========================
    # CREAZIONE FILE TEMU
    # =========================

    output_rows = []

    for _, row in df.iterrows():
        cap, qty = capacita_quantita(row.get("Formato (L)", ""))

        output_rows.append({
            "Categoria": 20416,
            "Nome della categoria": "",
            "Tipo di articolo": "",
            "Nome dell'Articolo": nome_articolo(row),
            "outGoodsSn": clean_outgoods(row.get("Codice prodotto","")),
            "outSkuSn": row.get("Sku",""),
            "Aggiorna o aggiungi": "Aggiorna/Aggiungi nuovo",
            "Marca": row.get("Marca",""),
            "Marchio": "",
            "Descrizione dell'articolo": row.get("Descrizione",""),
            "Punto elenco 1": "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici.",
            "Punto elenco 2": row.get("Descrizione breve",""),
            "Punto elenco 3": bullet_formato(row.get("Formato (L)",""), row.get("Sku","")),
            "Punto elenco 4": "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione.",
            "URL Img 1": row.get("Img 1",""),
            "URL Img 2": row.get("Img 2",""),
            "URL Img 3": row.get("Img 3",""),
            "URL Img 4": row.get("Img 4",""),
            "URL Img 5": row.get("Img 5",""),
            "URL Img 6": row.get("Img 6",""),
            "URL Img 7": row.get("Img 7",""),
            "Tema della variante": "Capacità × Quantità",
            "Capacità": cap,
            "Quantità": qty,
            "URL immagini SKU 1": row.get("Img 1",""),
            "Quantità stock": 10,
            "Prezzo base - EUR": round((row.get("Prezzo Marketplace",0)/1.22)*0.85,2),
            "Prezzo di listino - EUR": row.get("Prezzo Marketplace",0),
            "Peso pacco - g": int(row.get("Formato (L)",1)*1000),
            "Lunghezza - cm": 25,
            "Larghezza - cm": 25,
            "Altezza - cm": 25,
            "Modello di spedizione": "Free",
            "Paese/Regione di origine": "Italy",
            "Produttore": produttore(row.get("Marca","")),
            "Persona responsabile per l'UE.": "LONG LIFE CONSULTING S.R.L."
        })

    # Creiamo il DataFrame finale rispettando tutte le colonne Temu
    df_out = pd.DataFrame(output_rows, columns=temu_columns)

    # =========================
    # EXPORT EXCEL
    # =========================
    buffer = BytesIO()
    df_out.to_excel(buffer, index=False)
    st.success("✅ File Temu generato correttamente")
    st.download_button(
        "⬇️ Scarica file Temu",
        data=buffer.getvalue(),
        file_name="listino_temu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
