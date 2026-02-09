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
        return "Fusto da 205L"
    return f"{fmt}L"

def bullet_formato(fmt, sku):
    """Punto elenco 3, con regola speciale per SKU contenente 'tan'"""
    try:
        fmt = int(fmt)
    except:
        return ""
    
    sku_lower = str(sku).lower() if sku else ""
    
    if "tan" in sku_lower:
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

def nome_articolo(row):
    parts = []
    for col in ["Sottocategoria", "Viscosità", "Marca", "ACEA"]:
        if col in row and pd.notna(row[col]):
            parts.append(str(row[col]))
    # Formato
    if "Formato (L)" in row and pd.notna(row["Formato (L)"]):
        parts.append(formato_label(row["Formato (L)"]))
    # Utilizzo
    if "Utilizzo" in row and pd.notna(row["Utilizzo"]):
        parts.append(str(row["Utilizzo"]))
    return " ".join(parts)

# =========================
# UPLOAD FILE
# =========================

file = st.file_uploader("📤 Carica il file Excel di input", type=["xlsx"])

if file:
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()  # pulizia nomi colonne
    st.subheader("Anteprima file input")
    st.dataframe(df.head())

    output_rows = []

    for _, row in df.iterrows():
        cap, qty = capacita_quantita(row.get("Formato (L)", 0))
        
        output_row = {
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
            "Punto elenco 3": bullet_formato(row.get("Formato (L)", 0), row.get("Sku", "")),
            "Punto elenco 4": "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione.",
            "Tema della variante": "Capacità × Quantità",
            "Colore": "",
            "Dimensioni": "",
            "Stile": "",
            "Materiale": "",
            "Sapori": "",
            "Persone applicabili": "",
            "Capacità": cap,
            "Composizione": "",
            "Peso": "",
            "Elementi": "",
            "Quantità": qty,
            "Modello": "",
            "Lunghezza dei capelli": "",
            "URL immagini SKU": row.get("Img 1", ""),
            "Quantità": 10,
            "Prezzo base - EUR": round((row.get("Prezzo Marketplace", 0) / 1.22) * 0.85, 2),
            "Link di riferimento": "",
            "Prezzo di listino - EUR": row.get("Prezzo Marketplace", 0),
            "Non disponibile per il prezzo di listino": "",
            "Peso pacco - g": int(row.get("Formato (L)", 0) * 1000) if pd.notna(row.get("Formato (L)", 0)) else "",
            "Lunghezza - cm": 25,
            "Larghezza - cm": 25,
            "Altezza - cm": 25,
            "Tipo SKU": "",
            "In confezione singola": "",
            "Quantità confezioni totale": "",
            "Unità di imballaggio": "",
            "Contenuto netto": "",
            "Contenuto netto totale": "",
            "Unità di contenuto netto": "",
            "Modello di spedizione": "Free",
            "Paese/Regione di origine": "Italy",
            "Provincia di origine": "",
            "Informazioni sulla confezione SKU (con etichetta visibile)": "",
            "Etichetta di origine e informazioni sul produttore": "",
            "Degli articoli con questo ID articolo sono stati immessi sul mercato dell'Unione Europea (o dell'Irlanda del Nord) dopo il 13 dicembre 2024?": "",
            "Identificazione dell'articolo": "",
            "Produttore": produttore(row.get("Marca", "")),
            "Persona responsabile per l'UE": "LONG LIFE CONSULTING S.R.L."
        }

        # =========================
        # Gestione immagini dettagli in colonne separate
        for i in range(1, 8):
            col = f"Img {i}"
            out_col = f"URL delle immagini dei dettagli {i}"
            output_row[out_col] = row[col] if col in row and pd.notna(row[col]) else ""

        output_rows.append(output_row)

    df_out = pd.DataFrame(output_rows)

    # =========================
    # Riordina le colonne secondo il tuo ordine
    colonne_ordine = [
        "Categoria","Nome della categoria","Tipo di articolo","Nome dell'Articolo",
        "outGoodsSn","outSkuSn","Aggiorna o aggiungi","Marca","Marchio","Descrizione dell'articolo",
        "Punto elenco 1","Punto elenco 2","Punto elenco 3","Punto elenco 4",
        "URL delle immagini dei dettagli 1","URL delle immagini dei dettagli 2","URL delle immagini dei dettagli 3",
        "URL delle immagini dei dettagli 4","URL delle immagini dei dettagli 5","URL delle immagini dei dettagli 6",
        "URL delle immagini dei dettagli 7",
        "Tema della variante","Colore","Dimensioni","Stile","Materiale","Sapori","Persone applicabili",
        "Capacità","Composizione","Peso","Elementi","Quantità","Modello","Lunghezza dei capelli",
        "URL immagini SKU","Quantità","Prezzo base - EUR","Link di riferimento","Prezzo di listino - EUR",
        "Non disponibile per il prezzo di listino","Peso pacco - g","Lunghezza - cm","Larghezza - cm",
        "Altezza - cm","Tipo SKU","In confezione singola","Quantità confezioni totale","Unità di imballaggio",
        "Contenuto netto","Contenuto netto totale","Unità di contenuto netto","Modello di spedizione",
        "Paese/Regione di origine","Provincia di origine","Informazioni sulla confezione SKU (con etichetta visibile)",
        "Etichetta di origine e informazioni sul produttore",
        "Degli articoli con questo ID articolo sono stati immessi sul mercato dell'Unione Europea (o dell'Irlanda del Nord) dopo il 13 dicembre 2024?",
        "Identificazione dell'articolo","Produttore","Persona responsabile per l'UE"
    ]

    df_out = df_out[colonne_ordine]

    # =========================
    # EXPORT EXCEL
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_out.to_excel(writer, sheet_name="Temu", index=False)

    st.success("✅ File Temu generato correttamente")
    st.download_button(
        "⬇️ Scarica file Temu",
        data=buffer.getvalue(),
        file_name="listino_temu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
