"""
We don't initially need i18n support, but it will be pretty useful once we do
if we collect all the strings in here.
"""

plugin_name = "Gaia"

project_start_open_button = "Öppna projekt"
project_start_create_button = "Skapa projekt"
project_start_draw_on_map = "Select an area on map"
project_start_settings_button = "Inställningar"
project_settings_validate_and_save_button = "Verifiera och spara"
project_settings_validate_empty_url_error = "URL kan inte vara tom"
project_settings_validate_invalid_url_error = "Texten är inte en giltig URL"
project_settings_validate_ping_error = (
    "Kunde inte nå Gaia backend, är du säker på att du har rätt adress?"
)
project_settings_validate_unknown_error = (
    "Något gick fel, försök igen om några minuter."
)
project_settings_validate_geoserver_ping_error = (
    "Kunde inte nå Geoserver, är du säker på att du har rätt adress?"
)

project_home_button = "Till startsida"
project_next_button = "Nästa"
project_back_button = "Tillbaka"
project_download_result_button = "Download result"
project_save_result_dialog = "Save result"
project_description = "Beskrivning"
project_description_error = "Du måste ange en beskrivning"
project_name = "Projektnamn"
project_name_error = "Du måste ange ett projektnamn"
project_wms_url = "WMS url"
project_wms_url_error = "Du måste ange en giltig WMS-URL"
project_wms_url_hint = "http://127.0.0.1:8000/geoserver/wms"
project_layer_name = "Lagernamn"
project_layer_name_error = "Du måste ange ett lagernamn"
project_layer_name_hint = "Lagernamn i WMS"
project_coordinate_system = "Koordinatsystem (EPSG)"
project_coordinate_system_error = "Du måste ange ett giltigt koordinatsystem"
project_coordinate_system_hint = "EPSG:xxxx"
project_mpp = "Bildupplösning (meter per pixel)"
project_mpp_error = "Du måste ange en giltig upplösning"
project_mpp_hint = "m/px"
product_delete_run_title = "Ta bort körning?"
product_delete_run_description = "Är du säker på att du vill ta bort körningen?"
project_create_new_run = "Skapa ny körning"
project_of = "av"

project_run_table_header = "Körningar"
project_run_table_header_name = "Namn"
project_run_table_header_last_update = "Senast ändrad"
project_run_table_header_status = "Status"
project_run_table_download_results = "Ladda ner resultat"
project_run_table_delete_run = "Ta bort körning"
project_run_execution_ongoing = "Pågår ..."
project_run_param_information = "Körningsinformation"

project_table_name = "Namn"
project_table_timestamp = "Skapad"
project_table_description = "Beskrivning"
project_table_delete_run = "Ta bort projekt"
project_delete_title = "Ta bort projekt?"
project_delete_description = "Är du säker på att du vill ta bort projektet?"

project_view_header = "Projekt"

settings_dialog_title = "Gaia - Inställningar"
settings_dialog_save_button = "Spara"
settings_dialog_cancel_button = "Avbryt"
settings_dialog_backend_url = "Gaia backend URL"
settings_dialog_local_geoserver_url = "Local GeoServer URL"
settings_dialog_api_key = "API-nyckel"
settings_dialog_clear_wms_approvals = "Glöm godkända WMS-servrar"
project_settings_validate_empty_api_key_error = (
    "API-nyckel kan inte vara tom. Du hittar den i serverns GAIA_API_KEY."
)
project_settings_validate_api_key_error = (
    "API-nyckeln avvisades av servern. Kontrollera att den är identisk med "
    "GAIA_API_KEY på servern."
)
project_settings_reenter_api_key_error = (
    "Backend-adressen har ändrats. Ange API-nyckeln igen så att den gamla "
    "nyckeln inte skickas till en ny server av misstag."
)

project_settings_https_required_error = (
    "HTTPS krävs för backend-adresser utanför lokalt nätverk. API-nyckeln "
    "skulle annars skickas okrypterad."
)

project_create_dialog_title = "Skapa nytt GAIA projekt"


project_create_run_back_button = "Körningar"
project_create_run_body_header = "Parametrar"
project_create_run_map_source = "Datakälla"
project_create_run_name_label = "Ange namn på körning"
project_create_run_name_hint = "Område namn"
project_create_run_name_error = "Namn måste vara minst 3 tecken"
project_create_run_select_area_label = "Välj ditt område"
project_create_run_select_area_button = "Markera aktuell vy"
project_create_run_select_area_error = "Bbox måste vara i formatet: minx,miny,maxx,maxy"
project_create_run_select_input_label = "Ange koordinater"
project_create_run_confidence_level_label = "Välj konfidensenivå"
project_create_run_confidence_level_hint = "75"
project_create_run_confidence_level_error = "Konfidensenivå måste vara mellan 0 och 100"
project_create_run_overlap_label = "Överlappning"
project_create_run_overlap_hint = "10"
project_create_run_overlap_error = "Överlappning måste vara mellan 0 och 50"
project_create_run_choose_model_label = "Välj objektyper"
project_create_run_execute_button = "Kör"
project_create_run_model_buildings = "Byggnader"
project_create_run_model_roads = "Vägar"
project_create_run_model_vegetation = "Skogsparti"
project_create_run_model_error = "Minst 1 objekt måste väljas"

project_run_status_title = "Segmentering/vektorisering pågår"
project_run_status_pending = "Väntar"
project_run_status_queued = "Köad"
project_run_status_running = "Pågår"
project_run_status_finished = "Klar"
project_run_status_error = "Fel"
project_run_status_killed = "Dödad"
project_run_status_unknown = "Okänd"
project_run_status_calculating = "Beräknar"

project_run_info_title = "Körningsinformation"
project_run_info_name = "Körningsnamn"
project_run_info_status = "Status"
project_run_info_selected_area = "Valt område (minX, maxY, maxX, minY)"
project_run_info_confidence_level = "Konfidensenivå"
project_run_info_overlap = "Överlappning"
project_run_info_chosen_models = "Valda objekt"

project_run_download_results_starting = "Laddar ned filer.. \nDenna operation kan ta flera minuter och QGIS kan bli långsamt eller oresponsivt under denna tid."
project_run_download_results_downloaded = "Filer nedladdade.."
project_run_download_results_unzipping = "Packar upp filer.."
project_run_download_results_adding_layers = "Lägger till lager i QGIS.."
project_run_download_results = "Hämtar resultat från GAIA"
project_run_download_hint = "Hämtar resultat från GAIA. Denna operation kan ta flera minuter och QGIS kan bli långsamt eller oresponsivt under denna tid."

## Help texts

project_start_help_title = "Konfigurering av Gaia plugin"
project_start_help_description = "För att använda Gaia plugin måste du konfigurera pluginens inställningar. Detta gör du genom att klicka på knappen 'Inställningar'."
project_start_help_description_pt2 = "För att ställa in pluginet krävs det att du har en address till Gaia backend och en address till din lokala Geoserver."

## Errors and messages

generic_error_title = "Något gick fel"
project_error_message = (
    "Det gick inte att skapa projektet, försök igen om några minuter."
)
project_delete_error_message = (
    "Det gick inte att ta bort projektet, försök igen om några minuter."
)
