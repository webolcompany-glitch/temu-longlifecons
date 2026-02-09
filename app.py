import streamlit as st
import pandas as pd

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
        formato_label(row.get("Formato (L)", "")),
        str(row.get("Utilizzo",""))
    ]
    return " ".join([p for p in parts if p])

# =========================
# UPLOAD FILE TEMPLATE TEMU
# =========================

file = st.file_uploader("📤 Carica il Template Temu ufficiale", type=["xlsx"])

if file:
    # Legge SOLO il foglio "Template - quello da compilare"
    df_template = pd.read_excel(file, sheet_name="Template - quello da compilare")
    st.subheader("Anteprima Template Temu")
    st.dataframe(df_template.head())

    # =========================
    # POPOLA LE COLONNE
    # =========================
    df = df_template.copy()

    # Esempio delle colonne da aggiornare
    df["Nome dell'Articolo"] = df.apply(nome_articolo, axis=1)
    df["outGoodsSn"] = df["Codice prodotto"].apply(clean_outgoods)
    df["outSkuSn"] = df["Sku"]
    df["Aggiorna o aggiungi"] = "Aggiorna/Aggiungi nuovo"
    df["Marca"] = df["Marca"]
    df["Marchio"] = ""
    df["Descrizione dell'articolo"] = df["Descrizione"]
    df["Punto elenco"] = "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici."
    df["Punto elenco 2"] = df["Descrizione breve"]
    df["Punto elenco 3"] = df.apply(lambda r: bullet_formato(r["Formato (L)"], r["Sku"]), axis=1)
    df["Punto elenco 4"] = "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione."
    for i in range(1,8):
        df[f"URL delle immagini dei dettagli {i}"] = df.get(f"Img {i}", "")
    df["Tema della variante"] = "Capacità × Quantità"
    cap_qty = df["Formato (L)"].apply(capacita_quantita)
    df["Capacità"] = cap_qty.apply(lambda x: x[0])
    df["Quantità"] = cap_qty.apply(lambda x: x[1])
    df["URL immagini SKU"] = df["Img 1"]
    df["Quantità stock"] = 10
    df["Prezzo base - EUR"] = round((df["Prezzo Marketplace"]/1.22)*0.85, 2)
    df["Prezzo di listino - EUR"] = df["Prezzo Marketplace"]
    df["Peso pacco - g"] = df["Formato (L)"]*1000
    df["Lunghezza - cm"] = 25
    df["Larghezza - cm"] = 25
    df["Altezza - cm"] = 25
    df["Modello di spedizione"] = "Free"
    df["Paese/Regione di origine"] = "Italy"
    df["Produttore"] = df["Marca"].apply(produttore)
    df["Persona responsabile per l'UE"] = "LONG LIFE CONSULTING S.R.L."

    # =========================
    # SALVA FILE
    # =========================
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Template - quello da compilare", index=False)
    st.success("✅ File Temu aggiornato pronto")
    st.download_button(
        "⬇️ Scarica file Temu aggiornato",
        data=buffer.getvalue(),
        file_name="listino_temu_compilato.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
