import datetime
import urllib.request
import os
import math
from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties, TableCellProperties, TableProperties
from odf.table import Table, TableColumn, TableRow, TableCell
from odf.text import H, P, LineBreak, Span
from odf.draw import Frame, Image


def download_logo(url="http://jkiesenhofer.bplaced.net/lambda/logo.png", save_path="logo.png"):
    try:
        urllib.request.urlretrieve(url, save_path)
        return save_path
    except Exception as e:
        print(f"Hinweis: Logo konnte nicht geladen werden ({e}). Bericht wird ohne Logo erstellt.")
    return None


def add_style(doc, name, family, fontsize=None, fontweight=None, color=None,
              fontfamily="Arial", italic=False, margin_top=None, margin_bottom=None,
              border_bottom=None, background_color=None):
    s = Style(name=name, family=family)
    tp_kwargs = {}
    if fontsize:     tp_kwargs["fontsize"] = fontsize
    if fontweight:   tp_kwargs["fontweight"] = fontweight
    if color:        tp_kwargs["color"] = color
    if fontfamily:   tp_kwargs["fontfamily"] = fontfamily
    if italic:       tp_kwargs["fontstyle"] = "italic"
    if tp_kwargs:
        s.addElement(TextProperties(**tp_kwargs))
    pp_kwargs = {}
    if margin_top:      pp_kwargs["margintop"] = margin_top
    if margin_bottom:   pp_kwargs["marginbottom"] = margin_bottom
    if border_bottom:   pp_kwargs["borderbottom"] = border_bottom
    if background_color: pp_kwargs["backgroundcolor"] = background_color
    if pp_kwargs:
        s.addElement(ParagraphProperties(**pp_kwargs))
    doc.styles.addElement(s)
    return s


def add_table_cell_style(doc, name, background_color=None, bold=False):
    s = Style(name=name, family="table-cell")
    if background_color:
        s.addElement(TableCellProperties(backgroundcolor=background_color))
    doc.styles.addElement(s)
    return s


def make_table(doc, rows, col_count, body_style, header_bg="#003366", row_bg_alt="#EAF1FB"):
    t = Table()
    for _ in range(col_count):
        t.addElement(TableColumn())

    _style_counter = [0]

    def next_id():
        _style_counter[0] += 1
        return _style_counter[0]

    for i, row_data in enumerate(rows):
        tr = TableRow()
        for j, text in enumerate(row_data):
            tc = TableCell()
            if i == 0:
                # Header: white bold text on dark background
                inner_style = Style(name=f"hdr_txt_{next_id()}", family="text")
                inner_style.addElement(TextProperties(fontweight="bold", color="#FFFFFF",
                                                      fontfamily="Arial", fontsize="10pt"))
                doc.styles.addElement(inner_style)
                p2 = P()
                span = Span(stylename=inner_style)
                span.addText(str(text))
                p2.addElement(span)
                cs_name = f"cs_hdr_{next_id()}"
                cell_style = Style(name=cs_name, family="table-cell")
                cell_style.addElement(TableCellProperties(backgroundcolor=header_bg, padding="0.1cm"))
                doc.styles.addElement(cell_style)
                tc = TableCell(stylename=cell_style)
                tc.addElement(p2)
            else:
                bg = row_bg_alt if i % 2 == 0 else "#FFFFFF"
                cs_name = f"cs_{next_id()}"
                cell_style = Style(name=cs_name, family="table-cell")
                cell_style.addElement(TableCellProperties(backgroundcolor=bg, padding="0.1cm"))
                doc.styles.addElement(cell_style)
                tc = TableCell(stylename=cell_style)
                p = P(stylename=body_style)
                p.addText(str(text))
                tc.addElement(p)
            tr.addElement(tc)
        t.addElement(tr)
    return t


def create_flotation_report(filename="Lambda_Flotationsanlage_Auslegungsbericht.odt"):
    doc = OpenDocumentText()

    # ── Styles ──────────────────────────────────────────────────────────────
    h1 = add_style(doc, "ReportH1", "paragraph", fontsize="20pt", fontweight="bold",
                   color="#003366", margin_top="0.5cm", margin_bottom="0.3cm",
                   border_bottom="0.05cm solid #003366")
    h2 = add_style(doc, "ReportH2", "paragraph", fontsize="14pt", fontweight="bold",
                   color="#003366", margin_top="0.4cm", margin_bottom="0.15cm")
    h3 = add_style(doc, "ReportH3", "paragraph", fontsize="12pt", fontweight="bold",
                   color="#336699", margin_top="0.25cm", margin_bottom="0.1cm")
    body = add_style(doc, "ReportBody", "paragraph", fontsize="10pt", margin_bottom="0.1cm")
    body_it = add_style(doc, "ReportBodyIt", "paragraph", fontsize="10pt",
                        italic=True, color="#444444")
    caption = add_style(doc, "ReportCaption", "paragraph", fontsize="9pt",
                        italic=True, color="#555555", margin_bottom="0.2cm")
    note = add_style(doc, "ReportNote", "paragraph", fontsize="9pt",
                     color="#7B7B7B", italic=True)
    separator = add_style(doc, "ReportSep", "paragraph", fontsize="4pt",
                          margin_top="0.2cm", margin_bottom="0.2cm",
                          border_bottom="0.03cm solid #CCCCCC")

    def p(text="", style=None):
        el = P(stylename=style or body)
        if text:
            el.addText(text)
        doc.text.addElement(el)

    def h(level, text, style):
        doc.text.addElement(H(outlinelevel=level, stylename=style, text=text))

    def sep():
        doc.text.addElement(P(stylename=separator))

    # ── Logo ──────────────────────────────────────────────────────────────
    logo_file = download_logo()
    if logo_file and os.path.exists(logo_file):
        try:
            href = doc.addPicture(logo_file)
            frame = Frame(width="5cm", height="1.8cm", anchortype="as-char")
            frame.addElement(Image(href=href))
            pl = P(stylename=body)
            pl.addElement(frame)
            doc.text.addElement(pl)
        except Exception as e:
            print(f"Logo-Fehler: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # DECKBLATT-INFO
    # ═══════════════════════════════════════════════════════════════════════
    p()
    h(1, "Lambda Consulting GmbH", h1)
    h(1, "Technischer Auslegungsbericht: Dissolved Air Flotation (DAF)", h1)
    p()

    meta = [
        ("Projekttitel:",       "Dimensionierung einer DAF-Anlage zur Industrieabwasserbehandlung"),
        ("Auftraggeber:",       "Muster Industrie AG"),
        ("Bearbeiter:",         "Dipl.-Ing. J. Kiesenhofer, Lambda Consulting GmbH"),
        ("Bericht-Nr.:",        "LC-DAF-2024-001"),
        ("Version:",            "1.0 – Vorentwurf"),
        ("Erstellungsdatum:",   datetime.datetime.now().strftime("%d.%m.%Y %H:%M Uhr")),
        ("Vertraulichkeit:",    "Intern / Nur für Projektbeteiligte"),
    ]
    meta_tbl = make_table(doc, [["Metadaten", ""]] + [[k, v] for k, v in meta],
                          2, body, header_bg="#003366")
    doc.text.addElement(meta_tbl)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 1. ZUSAMMENFASSUNG
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "1. Zusammenfassung (Executive Summary)", h2)
    p("Der vorliegende Bericht dokumentiert die verfahrenstechnische Auslegung einer Dissolved-Air-Flotations-"
      "anlage (DAF) für die Behandlung von Industrieabwasser. Ziel der Anlage ist die Abtrennung von "
      "suspendierten Feststoffen, Ölen, Fetten und kolloidalen Partikeln aus dem Prozessabwasser, um "
      "gesetzliche Einleitgrenzwerte zuverlässig einzuhalten.", body)
    p()
    p("Die Anlage ist für einen Bemessungsvolumenstrom von 120 m³/h ausgelegt und erzielt bei korrektem "
      "Betrieb Abscheideleistungen >95 % für flotierbare Inhaltsstoffe. Die Dimensionierung basiert auf "
      "anerkannten Regeln der Technik gemäß ATV-Merkblatt M 605 sowie DIN EN 12255-5.", body)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 2. GRUNDLAGEN DAF-VERFAHREN
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "2. Verfahrenstechnische Grundlagen der DAF", h2)

    h(3, "2.1 Funktionsprinzip", h3)
    p("Bei der Dissolved Air Flotation (gelöste-Luft-Flotation) wird ein Teil des gereinigten Ablaufs "
      "(Rezirkulatstrom) unter Druck (4–6 bar) mit Luft gesättigt. Beim Entspannen dieses Druckwassers "
      "auf atmosphärischen Druck entstehen feinste Mikroblasen (Ø 10–100 µm), die an Partikel anhaften "
      "und diese durch ihren Auftrieb an die Oberfläche tragen, wo der Schwimmschlamm mechanisch "
      "abgeräumt wird.", body)
    p()
    p("Zur Verbesserung der Abscheideleistung wird dem Zulauf eine Fällungs- und Flockungschemikalie "
      "(z. B. Aluminiumsulfat oder FeCl₃ sowie Flockungshilfsmittel) zugegeben, die eine "
      "Destabilisierung der Kolloidpartikel und Ausbildung kompakter Flocken bewirkt.", body)

    h(3, "2.2 Verfahrensschema (vereinfacht)", h3)
    p("Zulauf → Vorsiebbung (Feinrechen, d < 3 mm) → pH-Korrektur → Fällung/Flockung (Mischkammer) → "
      "DAF-Becken (Flotationszone + Klärzone) → Ablauf → Rezirkulation (15–30 %) → Druckbehälter "
      "(Sättigerdruck ~5 bar) ↻", body_it)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 3. EINGANGSPARAMETER
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "3. Verfahrenstechnische Eingangsparameter", h2)

    # ---- Kernparameter ----
    Q          = 120.0      # Volumenstrom m³/h
    t_R        = 25.0       # Verweilzeit min
    c_solid    = 2.5        # Feststoffgehalt g/l
    q_A        = 5.0        # Flächenbelastung m³/(m²·h)
    temp       = 18.0       # Wassertemperatur °C
    pH_roh     = 7.8        # Roh-pH
    pH_ziel    = 6.5        # Ziel-pH für Fällung
    c_oil      = 150.0      # Öl/Fett-Gehalt mg/l
    c_CSB      = 380.0      # CSB mg/l
    c_BSB5     = 95.0       # BSB5 mg/l
    turbidity  = 220.0      # Trübung NTU
    p_sat      = 5.0        # Sättigerdruck bar (abs)
    recycle_r  = 0.20       # Rezirkulationsrate (Anteil von Q)
    eta_sat    = 0.85       # Sättigungsgrad Luft im Druckbehälter
    rho_water  = 1000.0     # kg/m³
    rho_solid  = 2650.0     # kg/m³ (Sand-/Mineralanteil)

    # Einleitgrenzwerte (fiktiv, beispielhaft)
    limit_AFS  = 30.0       # mg/l
    limit_CSB  = 75.0       # mg/l
    limit_oil  = 10.0       # mg/l

    rows_in = [
        ["Parameter", "Symbol", "Wert", "Einheit", "Bemerkung"],
        ["Zulauf-Volumenstrom", "Q", Q, "m³/h", "Bemessungswert (100 %)"],
        ["Spitzenlast-Faktor", "f_peak", "1.25", "–", "Q_peak = 150 m³/h"],
        ["Hydraul. Verweilzeit", "t_R", t_R, "min", "DAF-Becken gesamt"],
        ["Spez. Flächenbelastung", "q_A", q_A, "m³/(m²·h)", "inkl. Rezirkulat"],
        ["Feststoffgehalt (AFS)", "c_AFS", c_solid, "g/l", "abfiltrierbare Stoffe"],
        ["Öl- und Fettgehalt", "c_Öl", c_oil, "mg/l", "nach Kohlenwasserstoffe"],
        ["CSB Rohwasser", "c_CSB", c_CSB, "mg/l", "Chemischer Sauerstoffbedarf"],
        ["BSB5 Rohwasser", "c_BSB5", c_BSB5, "mg/l", "–"],
        ["Trübung Rohwasser", "NTU", turbidity, "NTU", "nephelometr. Trübungseinheit"],
        ["Rohwasser-pH", "pH_roh", pH_roh, "–", "Eingangsmesspunkt"],
        ["Ziel-pH Fällung", "pH_Fällung", pH_ziel, "–", "opt. Bereich 6.0–6.8"],
        ["Wassertemperatur", "T", temp, "°C", "Jahresmittelwert"],
        ["Sättigerdruck", "p_sat", p_sat, "bar (abs)", "Druckluft-Sättigung"],
        ["Rezirkulationsrate", "r", f"{int(recycle_r*100)} %", "–", "Anteil am Zulauf Q"],
    ]
    doc.text.addElement(make_table(doc, rows_in, 5, body))
    p()
    p(f"Einleitgrenzwerte (Indirekteinleitung): AFS ≤ {limit_AFS} mg/l | CSB ≤ {limit_CSB} mg/l | Öl ≤ {limit_oil} mg/l", note)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 4. BERECHNUNGEN
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "4. Auslegungsberechnungen", h2)

    # ---- 4.1 Beckenvolumen & Oberfläche ----
    h(3, "4.1 Beckenvolumen und Beckenoberfläche", h3)

    Q_m3s        = Q / 3600.0
    Q_recycle    = Q * recycle_r
    Q_total      = Q + Q_recycle
    volumen_m3   = Q * (t_R / 60.0)
    flaeche_m2   = Q_total / q_A
    tiefe_m      = volumen_m3 / flaeche_m2
    # Standard-Länge:Breite = 3:1
    breite_m     = math.sqrt(flaeche_m2 / 3.0)
    laenge_m     = 3.0 * breite_m
    # Ausführungsmaße (aufrunden auf 0.5 m)
    breite_rnd   = math.ceil(breite_m * 2) / 2
    laenge_rnd   = math.ceil(laenge_m * 2) / 2
    tiefe_rnd    = round(tiefe_m + 0.3, 1)   # + Freibord / Schlammzone

    p("Das Flotationsbecken wird als rechteckiges Betonbecken mit L:B = 3:1 ausgeführt. "
      "Das Gesamtvolumen berücksichtigt Flotations-, Klärzonen und Schlammraum.", body)
    p()

    rows_vol = [
        ["Größe", "Formel / Ansatz", "Ergebnis", "Einheit"],
        ["Rezirkulatstrom Q_R", f"r · Q = {recycle_r}·{Q}", f"{Q_recycle:.1f}", "m³/h"],
        ["Gesamtzulauf DAF", f"Q + Q_R", f"{Q_total:.1f}", "m³/h"],
        ["Erforderl. Flotationsvolumen", f"Q · t_R / 60", f"{volumen_m3:.2f}", "m³"],
        ["Erforderl. Beckenoberfläche", f"Q_ges / q_A = {Q_total:.0f}/{q_A}", f"{flaeche_m2:.2f}", "m²"],
        ["Mittlere Beckentiefe (berechnet)", f"V / A", f"{tiefe_m:.2f}", "m"],
        ["Beckenlänge (rechnerisch)", "√(A/3) × 3", f"{laenge_m:.2f}", "m"],
        ["Beckenbreite (rechnerisch)", "√(A/3)", f"{breite_m:.2f}", "m"],
        ["Beckenlänge (Ausführung, aufger.)", "–", f"{laenge_rnd:.1f}", "m"],
        ["Beckenbreite (Ausführung, aufger.)", "–", f"{breite_rnd:.1f}", "m"],
        ["Beckentiefe (Ausführung, m. Freibord)", "t + 0.30 m", f"{tiefe_rnd:.1f}", "m"],
    ]
    doc.text.addElement(make_table(doc, rows_vol, 4, body))

    # ---- 4.2 Feststoff- und Schlammbilanz ----
    h(3, "4.2 Feststoff- und Schlammbilanz", h3)

    feststoff_kg_h   = Q * c_solid                      # g/l × m³/h = kg/h
    eta_abscheid     = 0.95
    abgetrennt_kg_h  = feststoff_kg_h * eta_abscheid
    ts_schlamm       = 35.0                              # % TS im Flotationsschlamm
    schlamm_volumen  = abgetrennt_kg_h / (ts_schlamm / 100.0 * rho_water)  # m³/h
    schlamm_tag      = schlamm_volumen * 20              # Betriebsstunden/Tag

    p("Der Flotationsschlamm wird über ein motorisch angetriebenes Schaumräumersystem kontinuierlich "
      "in einen Schlammtrichter abgeführt. Der entwässerte Schlamm wird per Kammerfilterpresse auf "
      "~35 % TS entwässert.", body)
    p()

    rows_sludge = [
        ["Größe", "Wert", "Einheit"],
        ["Feststoffeintrag (Rohwasser)", f"{feststoff_kg_h:.1f}", "kg/h"],
        ["Abscheidegrad DAF", f"{int(eta_abscheid*100)} %", "–"],
        ["Abgetrennte Feststofffracht", f"{abgetrennt_kg_h:.1f}", "kg/h"],
        ["TS-Gehalt Flotationsschlamm", f"{ts_schlamm:.0f}", "%"],
        ["Schlammvolumenstrom", f"{schlamm_volumen:.3f}", "m³/h"],
        ["Schlammaufkommen/Tag (20 h/d)", f"{schlamm_tag:.2f}", "m³/d"],
    ]
    doc.text.addElement(make_table(doc, rows_sludge, 3, body))

    # ---- 4.3 Luft-Feststoff-Verhältnis ----
    h(3, "4.3 Luft-Feststoff-Verhältnis (A/S-Ratio)", h3)

    # Gelöste Luftmenge bei p_sat
    # Cs(T) ≈ 18.7 mg/L bei 18°C (Henry-Gesetz)
    Cs = 18.7 + (20.0 - temp) * 0.1   # vereinfachte Temperaturkorrektur
    # Gelöste Luft im Rezirkulatstrom
    air_dissolved_g_h = Q_recycle * eta_sat * Cs * (p_sat - 1.0)  # mg/L × m³/h → g/h
    # A/S-Ratio (g Luft / g Feststoff)
    AS_ratio = air_dissolved_g_h / (feststoff_kg_h * 1000.0)

    p("Das Luft-Feststoff-Verhältnis (Air-to-Solids Ratio, A/S) ist eine Schlüsselgröße für den "
      "Flotationserfolg. Empfohlener Bereich: 0.005 – 0.060 (optimum ~0.01).", body)
    p()

    rows_as = [
        ["Größe", "Formel / Wert", "Einheit"],
        ["Luftlöslichkeit bei 18 °C (Cs)", f"≈ {Cs:.1f}", "mg/L"],
        ["Sättigungsgrad (η_sat)", f"{eta_sat:.0%}", "–"],
        ["Sättigerdruck", f"{p_sat} bar (abs)", "–"],
        ["Effektive Druckstufe (p–1)", f"{p_sat-1:.1f} bar", "–"],
        ["Gelöste Luftmenge", f"{air_dissolved_g_h:.0f}", "g/h"],
        ["Feststoffeintrag", f"{feststoff_kg_h*1000:.0f}", "g/h"],
        ["A/S-Ratio", f"{AS_ratio:.4f}", "g Luft / g Feststoff"],
        ["Beurteilung", "✓ im empfohlenen Bereich" if 0.005 <= AS_ratio <= 0.060 else "⚠ außerhalb Empfehlung", "–"],
    ]
    doc.text.addElement(make_table(doc, rows_as, 3, body))

    # ---- 4.4 Chemikalienbedarf ----
    h(3, "4.4 Chemikalienbedarf Fällung / Flockung", h3)

    alum_dose_mg_l  = 45.0      # mg/L Aluminiumsulfat
    polymer_dose    = 2.5       # mg/L Polyacrylamid (Flockungshilfsmittel)
    caustic_dose    = 12.0      # mg/L NaOH für pH-Korrektur
    alum_kg_h       = alum_dose_mg_l * Q / 1000.0    # g/L * m³/h / 1000 = kg/h
    polymer_kg_h    = polymer_dose * Q / 1000.0
    caustic_kg_h    = caustic_dose * Q / 1000.0

    p("Aufgrund des erhöhten Öl-/Fettanteils und der Trübung wird eine zweistufige Chemikaliendosierung "
      "vorgesehen: Fällmittel (Aluminiumsulfat, Al₂(SO₄)₃) zur Koagulation, anschließend "
      "Flockungshilfsmittel (anionisches PAM) zur Flockenvergröberung.", body)
    p()

    rows_chem = [
        ["Chemikalie", "Dosis (mg/l)", "Verbrauch (kg/h)", "Verbrauch (kg/d, 20h)", "Lagerung"],
        ["Aluminiumsulfat Al₂(SO₄)₃ (17 %)", f"{alum_dose_mg_l:.0f}", f"{alum_kg_h:.2f}",
         f"{alum_kg_h*20:.1f}", "IBC 1.000 L"],
        ["Flockungshilfsmittel (anion. PAM)", f"{polymer_dose:.1f}", f"{polymer_kg_h:.3f}",
         f"{polymer_kg_h*20:.2f}", "Sack 25 kg"],
        ["NaOH (32 %) pH-Korrektur", f"{caustic_dose:.0f}", f"{caustic_kg_h:.2f}",
         f"{caustic_kg_h*20:.1f}", "IBC 1.000 L"],
    ]
    doc.text.addElement(make_table(doc, rows_chem, 5, body))
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 5. MASCHINENTECHNISCHE AUSRÜSTUNG
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "5. Maschinentechnische Ausrüstung", h2)

    rows_equip = [
        ["Position", "Komponente", "Auslegungsparameter", "Stk."],
        ["P-01/02", "Zulaufpumpe (Doppelanlage)", f"Q = {Q:.0f} m³/h, H ≥ 15 mWS, n+1-Redundanz", "2"],
        ["P-03", "Rezirkulationspumpe", f"Q_R = {Q_recycle:.0f} m³/h, H ≥ 6 bar", "1"],
        ["B-01", "Druckbehälter / Sättiger", f"V ≥ 0,5 m³, Betriebsdruck {p_sat} bar, ASME-zertif.", "1"],
        ["K-01", "Kompressor / Druckluft", "Luftbedarf ≥ 50 Nm³/h, p = 6 bar, ölgeschmiert", "1"],
        ["D-01/02/03", "Dosierpumpen (Membran)", "je Q_dos = 0–100 l/h, 6 bar, ATEX optional", "3"],
        ["R-01", "Feinrechen / Vorsiebbung", "Spaltweite 3 mm, selbstreinigend", "1"],
        ["AG-01", "Schaumräumer (Kettenräumer)", f"Breite {breite_rnd:.1f} m, Geschw. 0,1–0,5 m/min", "1"],
        ["A-01", "Online-Analysatoren (pH, Trb., Lf.)", "Kontaktelektrode + Optosensor, 4–20 mA", "3"],
        ["SPS-01", "Prozessleittechnik (SPS + SCADA)", "Siemens S7-1500, Fernzugriff via VPN", "1"],
    ]
    doc.text.addElement(make_table(doc, rows_equip, 4, body))
    p()
    p("Alle druckführenden Komponenten sind gemäß Druckgeräterichtlinie 2014/68/EU auszulegen "
      "und zu kennzeichnen. Elektrische Betriebsmittel in Gefahrenbereichen (Chemikalienlager) "
      "sind in ATEX-Schutzzone 2 einzuordnen.", note)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 6. ENERGIE- UND BETRIEBSKOSTEN
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "6. Energie- und Betriebskostenabschätzung", h2)

    p("Die folgende Abschätzung basiert auf Erfahrungswerten aus vergleichbaren DAF-Projekten "
      "(Lambda Consulting Datenbasis, 2019–2024). Alle Preisangaben sind Netto-Richtwerte.", body)
    p()

    # Energiebedarf
    P_pumps    = 7.5 + 5.5          # kW (Zulauf + Rezirk)
    P_compr    = 4.0                 # kW Kompressor
    P_misc     = 2.5                 # kW Räumer, Dosierpumpen, MSR
    P_total    = P_pumps + P_compr + P_misc
    h_per_year = 7000                # Betriebsstunden/Jahr
    energy_kwh = P_total * h_per_year
    price_kwh  = 0.20               # €/kWh
    cost_energy = energy_kwh * price_kwh

    chem_cost_yr   = (alum_kg_h * 0.18 + polymer_kg_h * 3.50 + caustic_kg_h * 0.22) * h_per_year
    sludge_ent_yr  = schlamm_tag * 250 * 85.0   # m³/d × 250 Betriebstage × 85 €/t
    maintenance_yr = 25000.0
    total_opex     = cost_energy + chem_cost_yr + sludge_ent_yr + maintenance_yr

    rows_cost = [
        ["Kostenposition", "Verbrauch/Jahr", "Einheitspreis", "Kosten/Jahr (€/a)"],
        ["Energie (gesamt)", f"{energy_kwh:,.0f} kWh/a", f"{price_kwh:.2f} €/kWh",
         f"{cost_energy:,.0f}"],
        ["Aluminiumsulfat", f"{alum_kg_h*h_per_year:,.0f} kg/a", "0.18 €/kg",
         f"{alum_kg_h*h_per_year*0.18:,.0f}"],
        ["PAM-Flockungsmittel", f"{polymer_kg_h*h_per_year:,.1f} kg/a", "3.50 €/kg",
         f"{polymer_kg_h*h_per_year*3.50:,.0f}"],
        ["NaOH (32 %)", f"{caustic_kg_h*h_per_year:,.0f} kg/a", "0.22 €/kg",
         f"{caustic_kg_h*h_per_year*0.22:,.0f}"],
        ["Schlammentsorgung", f"{schlamm_tag*250:,.0f} m³/a", "85 €/m³",
         f"{sludge_ent_yr:,.0f}"],
        ["Wartung & Instandhaltung", "Pauschal", "–", f"{maintenance_yr:,.0f}"],
        ["GESAMT-BETRIEBSKOSTEN", "–", "–", f"{total_opex:,.0f}"],
    ]
    doc.text.addElement(make_table(doc, rows_cost, 4, body))
    p()
    p(f"Spezifische Betriebskosten: ca. {total_opex / (Q * h_per_year):.3f} €/m³ behandeltes Abwasser.", note)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 7. REGELUNGSKONZEPT & MSR
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "7. Regelungskonzept und MSR-Technik", h2)

    p("Die Anlage wird vollautomatisch über eine speicherprogrammierbare Steuerung (SPS) betrieben. "
      "Die übergeordnete Prozessführung erfolgt per SCADA-System mit Fernzugriff. Folgende Regelkreise "
      "sind vorgesehen:", body)
    p()

    rows_ctrl = [
        ["Regelkreis", "Messgröße", "Stellgröße", "Regler-Typ"],
        ["pH-Regelung", "pH-Elektrode (Einlauf)", "NaOH-Dosierpumpe", "PID"],
        ["Fällmittel-Dosierung", "Volumenstrom Q (Einlauf)", "Al₂(SO₄)₃-Dosierpumpe", "Verhältnisregler"],
        ["Flockungsmittel", "Trübungssonde (Post-Flock.)", "PAM-Dosierpumpe", "PID + Trübungs-FF"],
        ["Sättigerdruck", "Druckgeber Sättiger", "Kompressor-Frequenzumrichter", "PID"],
        ["Rezirkulatstrom", "Volumenstrommes. Q_R", "Regelventil + FU Pumpe P-03", "Kaskade"],
        ["Schlammräumer", "Timer + Trübung (Ablauf)", "Motoransteuerung Räumer AG-01", "Zeit/Trüb."],
    ]
    doc.text.addElement(make_table(doc, rows_ctrl, 4, body))
    p()
    p("Online-Messung im Ablauf: pH, Trübung (NTU), elektrische Leitfähigkeit (µS/cm). "
      "Grenzwertüberschreitungen lösen Alarm aus und sperren ggf. die Ablauffreigabe.", note)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 8. NORMEN UND RICHTLINIEN
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "8. Angewandte Normen und Richtlinien", h2)

    rows_norms = [
        ["Norm / Richtlinie", "Titel", "Anwendungsbereich"],
        ["DIN EN 12255-5", "Abwasserbehandlungsanlagen – Flotation", "Beckenauslegung, Betrieb"],
        ["ATV-M 605", "Planung und Bau von DAF-Anlagen", "Flächenbelastung, A/S-Ratio"],
        ["AbwV Anhang 49", "Abwasserverordnung Mineralölhaltiges Abwasser", "Einleitgrenzwerte Öl/Fett"],
        ["DIN EN ISO 7027", "Bestimmung der Trübung", "Trübungsmessung"],
        ["DIN EN ISO 11885", "ICP-OES Wasseranalytik", "Spurenstoffüberwachung"],
        ["RL 2014/68/EU", "Druckgeräterichtlinie (PED)", "Druckbehälter, Sättiger"],
        ["ATEX RL 2014/34/EU", "Explosionsschutzrichtlinie", "Chemikalienlagerbereich"],
        ["VDI 2079", "Abwasserbehandlung – Flotation", "Verfahrenstechnik allgemein"],
    ]
    doc.text.addElement(make_table(doc, rows_norms, 3, body))
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 9. QUALITÄTSSICHERUNG UND PROBENAHME
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "9. Qualitätssicherung und Probenahmeplan", h2)

    p("Zur Sicherstellung der Einleitgrenzwerte und Dokumentation des Anlagenbetriebs wird ein "
      "strukturierter Probenahmeplan gemäß Behördenauflagen implementiert:", body)
    p()

    rows_qm = [
        ["Probenahmeort", "Parameter", "Häufigkeit", "Methode", "Grenzwert"],
        ["Zulauf (P-01)", "AFS, CSB, BSB5, Öl/Fett, pH", "wöchentlich", "24h-Mischprobe", "–"],
        ["Ablauf DAF (A-01)", "AFS, CSB, Öl/Fett, pH, Lf.", "täglich online + wöchentl. Labor", "Online + Stichprobe",
         f"AFS ≤{limit_AFS} | CSB ≤{limit_CSB} | Öl ≤{limit_oil} mg/l"],
        ["Schwimmschlamm", "TS, Glühverlust", "monatlich", "Stichprobe", "TS ≥ 25 %"],
        ["Sättiger-Ablass", "Eisengehalt, pH", "monatlich", "Stichprobe", "Fe ≤ 2 mg/l"],
    ]
    doc.text.addElement(make_table(doc, rows_qm, 5, body))
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 10. ZUSAMMENFASSUNG AUSLEGUNGSERGEBNISSE
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "10. Zusammenfassung aller Auslegungsergebnisse", h2)

    rows_final = [
        ["Kenngröße", "Wert", "Einheit"],
        ["Beckenabmessungen (L × B × T)", f"{laenge_rnd:.1f} × {breite_rnd:.1f} × {tiefe_rnd:.1f}", "m"],
        ["Flotationsbeckenvolumen (netto)", f"{volumen_m3:.1f}", "m³"],
        ["Beckenoberfläche (netto)", f"{flaeche_m2:.1f}", "m²"],
        ["Hydraulische Verweilzeit", f"{t_R:.0f}", "min"],
        ["Spez. Flächenbelastung q_A", f"{q_A:.1f}", "m³/(m²·h)"],
        ["Rezirkulatstrom Q_R", f"{Q_recycle:.0f}", "m³/h"],
        ["Luft-Feststoff-Verhältnis (A/S)", f"{AS_ratio:.4f}", "–"],
        ["Feststofffracht Zulauf", f"{feststoff_kg_h:.1f}", "kg/h"],
        ["Schlammaufkommen/Tag", f"{schlamm_tag:.2f}", "m³/d"],
        ["Installierte Leistung", f"{P_total:.1f}", "kW"],
        ["Jahresenergieverbrauch", f"{energy_kwh:,.0f}", "kWh/a"],
        ["Betriebskosten gesamt", f"{total_opex:,.0f}", "€/a"],
        ["Spez. Betriebskosten", f"{total_opex / (Q * h_per_year):.3f}", "€/m³"],
    ]
    doc.text.addElement(make_table(doc, rows_final, 3, body))
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # 11. FAZIT UND NÄCHSTE SCHRITTE
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "11. Fazit und nächste Schritte", h2)

    p("Die vorliegende Auslegung zeigt, dass eine DAF-Anlage nach den dargestellten Parametern "
      "die geforderten Reinigungsziele zuverlässig erfüllen kann. Das Luft-Feststoff-Verhältnis "
      f"von A/S = {AS_ratio:.4f} liegt im empfohlenen Bereich, und die gewählte Flächenbelastung "
      f"von {q_A} m³/(m²·h) entspricht dem Stand der Technik gemäß ATV-M 605.", body)
    p()
    p("Empfohlene nächste Schritte:", body)

    steps = [
        "Durchführung eines Jar-Tests zur Bestätigung der Fällmittel-Dosierung",
        "Einholung von Angeboten für Becken und Maschinentechnik (Ausschreibung)",
        "Abstimmung des Probenahmekonzepts mit der Genehmigungsbehörde",
        "Erstellung der Genehmigungsplanung (§ 58 WHG) inkl. Antragsunterlagen",
        "Festlegung des Standorts, Untergrunduntersuchung und Tragwerksplanung",
        "Detail-Engineering und Erstellung von RI-Fließbild (P&ID)",
    ]
    for s in steps:
        p(f"  • {s}", body)

    p()
    p("Für Rückfragen steht Lambda Consulting GmbH gerne zur Verfügung.", body_it)
    sep()

    # ═══════════════════════════════════════════════════════════════════════
    # ANHANG: GLOSSAR
    # ═══════════════════════════════════════════════════════════════════════
    h(2, "Anhang A: Glossar und Abkürzungsverzeichnis", h2)

    rows_gloss = [
        ["Abkürzung", "Bedeutung"],
        ["AFS", "Abfiltrierbare Stoffe (Feststoffkonzentration)"],
        ["A/S-Ratio", "Air-to-Solids Ratio – Luft-Feststoff-Verhältnis"],
        ["BSB5", "Biologischer Sauerstoffbedarf (5 Tage)"],
        ["CSB", "Chemischer Sauerstoffbedarf"],
        ["DAF", "Dissolved Air Flotation (Gelöste-Luft-Flotation)"],
        ["FU", "Frequenzumrichter"],
        ["MSR", "Mess-, Steuer- und Regelungstechnik"],
        ["NTU", "Nephelometric Turbidity Unit (Trübungseinheit)"],
        ["PAM", "Polyacrylamid (Flockungshilfsmittel)"],
        ["PED", "Pressure Equipment Directive (Druckgeräterichtlinie)"],
        ["SPS", "Speicherprogrammierbare Steuerung"],
        ["TS", "Trockensubstanzgehalt (Feststoffgehalt Schlamm)"],
        ["WHG", "Wasserhaushaltsgesetz"],
    ]
    doc.text.addElement(make_table(doc, rows_gloss, 2, body))
    p()
    p(f"Erstellt mit Lambda Consulting Report Engine · {datetime.datetime.now().strftime('%Y')} · "
      "Alle Angaben ohne Gewähr – Vorentwurfs-Stadium", note)

    # ── Speichern ──────────────────────────────────────────────────────────
    # Datei im aktuellen Arbeitsverzeichnis speichern (portabel)
    out = os.path.join(os.getcwd(), filename)
    doc.save(out)
    print(f"Bericht erfolgreich erstellt: {out}")
    return out


if __name__ == "__main__":
    create_flotation_report()
