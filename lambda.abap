REPORT z_create_vibration_damper.

DATA: ls_headdata    TYPE bapimathead,
      ls_clientdata  TYPE bapi_mara,
      ls_clientdatax TYPE bapi_marax,
      ls_plantdata   TYPE bapi_marc,
      ls_plantdatax  TYPE bapi_marcx,
      ls_valuation   TYPE bapi_mbew,
      ls_valuationx  TYPE bapi_mbewx,
      lt_material_descr TYPE TABLE OF bapi_makt,
      ls_material_descr TYPE bapi_makt,
      ls_return      TYPE bapiret2.

" 1. Kopfdaten: Materialnummer, Branche und Materialart
ls_headdata-material   = 'VIB-DAMPER-001'. " Materialnummer
ls_headdata-ind_sector = 'M'.               " Maschinenbau
ls_headdata-matl_type  = 'HAWA'.            " Handelsware (Trading Goods)
ls_headdata-basic_view = 'X'.
ls_headdata-purchase_view = 'X'.
ls_headdata-account_view  = 'X'.

" 2. Grunddaten (Client Level)
ls_clientdata-base_uom = 'ST'.              " Stück
ls_clientdata-matl_group = '001'.           " Warengruppe
ls_clientdatax-base_uom = 'X'.
ls_clientdatax-matl_group = 'X'.

" 3. Kurztext (Beschreibung)
ls_material_descr-langu = sy-langu.
ls_material_descr-matl_desc = 'Vibrationsdämpfer Gummi-Metall'.
APPEND ls_material_descr TO lt_material_descr.

" 4. Werksdaten
ls_plantdata-plant = '1000'.                " Ihr Werkscode
ls_plantdatax-plant = '1000'.

" 5. Buchhaltung / Bewertung (Preis festlegen)
ls_valuation-val_area  = '1000'.            " Bewertungskreis (meist = Werk)
ls_valuation-price_ctrl = 'S'.              " S = Standardpreis
ls_valuation-std_price  = '15.00'.          " Der gewünschte Preis
ls_valuation-val_class  = '3100'.           " Bewertungsklasse für Handelsware
ls_valuationx-val_area  = '1000'.
ls_valuationx-price_ctrl = 'X'.
ls_valuationx-std_price  = 'X'.
ls_valuationx-val_class  = 'X'.

" BAPI Aufruf
CALL FUNCTION 'BAPI_MATERIAL_SAVEDATA'
  EXPORTING
    headdata       = ls_headdata
    clientdata     = ls_clientdata
    clientdatax    = ls_clientdatax
    plantdata      = ls_plantdata
    plantdatax     = ls_plantdatax
    valuationdata  = ls_valuation
    valuationdatax = ls_valuationx
  IMPORTING
    return         = ls_return
  TABLES
    materialdescription = lt_material_descr.

" Commit oder Rollback
IF ls_return-type = 'S' OR ls_return-type = 'I'.
  CALL FUNCTION 'BAPI_TRANSACTION_COMMIT'
    EXPORTING
      wait = 'X'.
  WRITE: / 'Erfolg: Material', ls_headdata-material, 'wurde angelegt.'.
ELSE.
  WRITE: / 'Fehler:', ls_return-message.
ENDIF.
