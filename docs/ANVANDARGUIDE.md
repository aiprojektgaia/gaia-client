# Användarguide — GAIA i QGIS

Den här guiden vänder sig till dig som ska använda GAIA i QGIS. Du behöver inte
kunna programmera.

GAIA analyserar flygbilder och skapar kartlager med byggnader, vägar och
vegetation. Du markerar ett område i kartan, väljer vad som ska hittas, och får
tillbaka färdiga vektorlager i QGIS.

---

## Innan du börjar

Du behöver fyra saker från den som driftar GAIA:

| Uppgift | Exempel |
|---|---|
| Adress till GAIA-servern | `https://gaia.kommunen.se:8443` |
| GAIA:s rotcertifikat (om servern använder sitt eget) | Filen `gaia-root.crt` |
| API-nyckel | En lång slumpmässig teckensträng |
| Adress till GeoServer eller annan WMS-server | `http://gaia.kommunen.se:9600` |

Om du fick ett rotcertifikat: importera det i QGIS under **Inställningar →
Alternativ → Autentisering → Hantera certifikat → Utfärdare → Importera** och
markera det som betrott. Annars kan pluginet inte ansluta till servern.

API-nyckeln är ett lösenord. Skicka den inte via e-post eller chatt, och lägg
den inte i ett delat dokument.

Du behöver också **QGIS version 3.44 eller senare** i 3-serien. GAIA fungerar
inte i äldre versioner och inte heller i QGIS 4.

Kontrollera din version under **Hjälp → Om QGIS**.

---

## 1. Installera insticksmodulen

1. Öppna QGIS.
2. Välj **Insticksmoduler → Hantera och installera insticksmoduler**.
3. Välj fliken **Installera från ZIP**.
4. Bläddra fram filen `GaiaClient_<version>_<datum>.zip` och klicka
   **Installera insticksmodul**.
5. Stäng fönstret. GAIA-ikonen visas nu i verktygsraden.

---

## 2. Ställ in anslutningen

Detta gör du en gång.

1. Klicka på GAIA-ikonen.
2. Klicka **Inställningar**.
3. Fyll i:
   - **Gaia backend URL** — adressen till servern
   - **API-nyckel** — nyckeln du fått
   - **Local GeoServer URL** — om du fått en sådan
4. Klicka **Verifiera och spara**.

Insticksmodulen kontrollerar att servern svarar och att nyckeln är rätt innan
den sparar.

**Om du får ett felmeddelande:**

| Meddelande | Betyder |
|---|---|
| *Kunde inte nå Gaia backend* | Adressen är fel, eller servern är nere. Kontrollera adressen med driftansvarig. |
| *API-nyckeln avvisades av servern* | Nyckeln stämmer inte. Kontrollera att hela nyckeln kopierats, utan mellanslag i början eller slutet. |
| *Texten är inte en giltig URL* | Adressen måste börja med `http://` eller `https://`. |

---

## 3. Skapa ett projekt

Ett projekt är en mapp för ditt arbete. Du kan ha flera körningar i samma
projekt.

1. Klicka **Skapa projekt**.
2. Ange **Projektnamn** och **Beskrivning**.
3. Spara.

Befintliga projekt visas i listan när du öppnar GAIA.

---

## 4. Starta en körning

En körning är en analys av ett område.

1. Öppna projektet och klicka **Skapa ny körning**.
2. Fyll i parametrarna:

| Fält | Vad du anger |
|---|---|
| **Ange namn på körning** | Ett namn du känner igen, minst 3 tecken |
| **Välj ditt område** | Zooma till området i kartan och klicka **Markera aktuell vy**. Du kan också skriva koordinater. |
| **Välj konfidensnivå** | Hur säker analysen ska vara. Standard är 75. |
| **Överlappning** | Standard är 10. Ändra bara om du blivit ombedd. |
| **Välj objektyper** | Kryssa i det som ska hittas — Byggnader, Vägar, Skogsparti. Minst ett måste väljas. |

3. Klicka **Kör**.

### Om konfidensnivån

Konfidensnivån styr hur säker modellen måste vara innan något ritas ut.

- **Högre värde (t.ex. 90)** — färre objekt, men de som hittas är oftare rätt.
- **Lägre värde (t.ex. 60)** — fler objekt, men fler felaktiga.

Börja med 75. Får du för många felaktiga objekt, höj värdet och kör om.

### Välj inte ett för stort område

Arbetet växer med områdets **yta**. Ett dubbelt så brett område tar ungefär
fyra gånger så lång tid. Börja med ett litet område första gången för att se hur
lång tid det tar hos er.

Servern kör en körning i taget. Startar någon annan en körning samtidigt får den
vänta.

---

## 5. Följ körningen

Statusen uppdateras automatiskt.

| Status | Betyder |
|---|---|
| **Väntar** / **Köad** | Körningen väntar på sin tur |
| **Beräknar** | Förbereder — antalet steg är ännu inte känt |
| **Pågår** | Analysen körs |
| **Klar** | Färdig, resultatet kan hämtas |
| **Fel** / **Dödad** | Något gick fel — se nedan |

Du kan stänga fönstret och komma tillbaka senare. Körningen fortsätter på
servern.

---

## 6. Hämta resultatet

1. Klicka **Ladda ner resultat** vid den färdiga körningen.
2. Välj var filen ska sparas.
3. Lagren läggs automatiskt till i QGIS.

Hämtningen kan ta flera minuter, och **QGIS kan bli långsamt eller sluta svara
under tiden**. Det är normalt — vänta tills det är klart.

Resultatet är en GeoPackage-fil (`.gpkg`) med ett lager per objekttyp. Den kan
öppnas i QGIS igen senare, och delas med andra.

---

## Om något går fel

### Rutan "Välj objektyper" är tom

Servern rapporterar inga tillgängliga modeller. Detta är nästan alltid ett
serverproblem, inte ett fel du gjort. Kontakta driftansvarig och be dem
kontrollera GAIA-tjänstens loggar.

### Körningen får status Fel eller Dödad

Ett steg i analysen misslyckades. När ett steg misslyckas avbryts resten av
körningen — därför kan flera steg visas som **Dödad** även om bara ett gick
sönder.

Du kan prova att köra om med ett mindre område. Kvarstår felet, kontakta
driftansvarig och uppge körningens namn och ungefär när du startade den.

### Insticksmodulen syns inte efter installation

Kontrollera att den är ikryssad under **Insticksmoduler → Hantera och installera
insticksmoduler → Installerade**.

Om den inte går att aktivera är QGIS-versionen sannolikt för gammal. GAIA kräver
**QGIS 3.44 eller senare**.

### Allt slutade fungera efter en uppdatering

Om servern uppdaterats kan API-nyckeln ha bytts. Gå till **Inställningar**, fyll
i den nya nyckeln och spara.

---

## Bra att veta

- **Resultatet är ett förslag, inte en facit.** Modellerna har tränats på
  flygbilder och gör fel. Granska alltid resultatet innan det används som
  underlag för beslut.
- **Projekt och körningar delas** av alla som använder samma GAIA-server. Ni ser
  varandras arbete.
- **Ta bort körningar ni inte behöver.** Resultatfiler tar mycket plats på
  servern.
