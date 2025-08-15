# Application Evaluator 2.0 Spesifikaatio

## 1. Tavoitteet

*   **Modernisointi ja joustavuus:** Korvataan vanhentunut versio 1.0 uudella, joustavammalla ja helpommin ylläpidettävällä järjestelmällä. Tavoitteena on tukea erilaisia arviointiprosesseja, kuten erilaisia painotuksia, kriteerirakenteita ja näkyvyysasetuksia. Samalla työkalu laajennetaan kattamaan pelkän arvioinnin lisäksi hakemusten keruu ja raportointi.
*   **Parempi käyttökokemus:** Parannetaan sekä ylläpitäjien että arvioijien käyttöliittymiä. Tarjotaan ylläpitäjille selkeämmät hallintatyökalut (hyödyntäen esimerkiksi Djangon admin-käyttöliittymää) ja arvioijille intuitiivisempi sekä tehokkaampi arviointinäkymä. Jos käyttäjän ei tarvitse luoda kampanjoita, haasteita tai arvioijia, järjestelmää tulee voida käyttää pelkästään varsinaisen frontend-käyttöliitymän kautta.
*   **Laajennettu toiminnallisuus:**
    *   Tavoitteena tuoda hakemusten kerääminen osaksi järjestelmää (vaiheittainen toteutus).
    *   Mahdollistetaan monitasoiset arviointikriteerit (ryhmät ja alikriteerit).
    *   Lisätään kampanjataso hallinnoinnin helpottamiseksi.
    *   Mahdollistetaan kampanja- ja haastekohtainen käyttäjä- ja oikeushallinta.
    *   Lisätään tuki keskusteluille hakemusten yhteydessä.
    *   Parannetaan raportointia ja arviointiprosessin seurantaa.
*   **Tekniset parannukset:**
    *   Siirretään laskenta palvelimelle eli laskenta suoritetaan ainoastaan yhdessä paikassa.
    *   Mitään ei kovakoodata käyttöliittymän osaksi, kaikki määrittelyt tehdään backendin kautta.
    *   Tarjotaan kattava REST-rajapinta dataan.
    *   Varmistetaan tietokannan eheys ja auditointi aikaleimojen ja lokien avulla.
    *   Pidetään järjestelmä avoimena lähdekoodina (Open Source) ja mahdollistetaan sekä oma asennus että SaaS-malli.
*   **Objektiivisuus ja läpinäkyvyys:** Parannetaan arviointiprosessin objektiivisuutta ja läpinäkyvyyttä yhtenäistämällä kriteereitä ja tarjoamalla selkeät työkalut.
*   **Tehokkuus:** Lyhennetään arviointiaikaa ja vähennetään manuaalista työtä sekä virheitä.


## 2. Toiminnalliset vaatimukset

Application Evaluator 2.0:n tavoitteena on laajentaa version 1.0 toiminnallisuutta siirtymällä puhtaasta arviointityökalusta kattavammaksi järjestelmäksi, joka hallinnoi koko hakemusten elinkaarta aina niiden keräämisestä arviointiin ja raportointiin. Tämä laajennus voidaan toteuttaa vaiheittain tärkeimpien arviointiominaisuuksien valmistuttua. Versio 2.0 esittää jäsennellymmän tavan organisoida arviointiprosesseja kampanjoiden ja haasteiden avulla, sekä mahdollistaa monipuolisemman kriteeristön ja käyttäjäroolien hallinnan.

### 2.1. Olemassaolevat ominaisuudet (muutokset/poistot)
*   **Laajennus arvioinnista hakemusten hallintaan:** Järjestelmä ei ole enää pelkkä erillinen arviointityökalu, vaan sen on tarkoitus kattaa myös hakemusten (tai tarjousten, ehdotusten) vastaanottaminen ja hallinnointi osana kampanjoita ja haasteita (vaiheittainen toteutus).
*   **Arviointikriteerien rakenne:** Aiemmasta mallista, jossa oli `KriteeriRyhmä`-objekteja (jotka saattoivat muodostaa monitasoisen hierarkian) ja niihin liitettyjä `Kriteeri`-objekteja, siirrytään malliin, jossa on ainoastaan hierarkkisesti järjestettyjä `Arviointikriteeri`-objekteja (`tyyppi='RYHMÄ'` tai `tyyppi='KRITEERI'`). Tämä mahdollistaa joustavamman ja monitasoisen kriteeristön luomisen.
*   **Laskentalogiikan siirto:** Kaikki pisteiden laskenta (esim. painotukset, keskiarvot) siirretään käyttöliittymästä palvelinpäähän (backend), mikä parantaa suorituskykyä ja ylläpidettävyyttä.
*   **Raportointinäkymien uudistus:** Vanhentuneet tai vaikeasti tulkittavat visualisoinnit (kuten v1.0:n tutkakaavio) korvataan selkeämmillä esitystavoilla (esim. pylväsdiagrammit).
*   **Käyttöliittymän modernisointi:** Vanhentuneet käyttöliittymäkomponentit päivitetään moderneihin vastineisiin parantaen yleistä käyttökokemusta.

### 2.2. Uudet ominaisuudet
*   **Kampanja- ja haastehallinta:**
    *   Mahdollisuus luoda ja hallinnoida ylätason Kampanjoita (Haastekierroksia), jotka kokoavat yhteen useita Haasteita.
    *   Kampanja- ja haastekohtaiset asetukset (nimet, kuvaukset, aikataulut, tilat, arvioijien näkyvyysasetukset).
    *   Haasteiden kloonaus kampanjan sisällä asetusten ja kriteeristön kopioimiseksi.
*   **Hakemusten hallinta:**
    *   Hakemusten vastaanotto ja tallennus järjestelmään (perustiedot, sisältödata, liitetiedostot).
    *   Hakemusten tilan seuranta (esim. Luonnos, Lähetetty, Arvioinnissa, Hyväksytty, Hylätty).
    *   Mahdollisuus liittää hakemuksia tiettyihin haasteisiin.
*   **Liitetiedostojen käsittely:** Mahdollisuus liittää useita tiedostoja kuhunkin hakemukseen ja hallinnoida niitä.
*   **Hierarkkinen arviointikriteeristö:**
    *   Monitasoisten kriteerien ja kriteeriryhmien määrittely haastekohtaisesti.
    *   Kriteerikohtaiset asetukset (painokerroin, maksimipisteet, kynnysarvo).
*   **Arviointiprosessi:**
    *   Arvioijat voivat antaa pisteitä ja kommentteja spesifisille kriteereille hakemuskohtaisesti.
    *   Järjestelmä laskee painotetut kokonaispisteet automaattisesti.
*   **Granulaarinen käyttäjä- ja roolihallinta:**
    *   Useita käyttäjärooleja (esim. Ylläpitäjä, Kampanja-admin, Haaste-admin, Arvioija).
    *   Oikeuksien hallinta kampanja- ja haastetasolla (`KampanjaKayttaja`, `HaasteKayttaja`).
*   **Raportointi ja seuranta:** Ylläpitäjän seurantanäkymä arviointiprosessin etenemiselle kampanjoittain, haasteittain ja arvioijoittain. Yhteenvedot tuloksista.
*   **REST API:** Kattava ohjelmointirajapinta (API) järjestelmän toimintojen käyttämiseksi ja integroimiseksi muihin järjestelmiin.
*   **Hakemuskohtainen keskustelu (nice-to-have):** Mahdollisuus käydä ketjutettua keskustelua yksittäisten hakemusten yhteydessä (roolien ja asetusten mukaisesti).
*   ~~**Organisaatioiden hallinta (nice-to-have):** Mahdollisuus linkittää kampanjoita ja käyttäjiä organisaatioihin.~~

## 3. Ei-toiminnalliset vaatimukset

*Kuvaa vaatimukset liittyen suorituskykyyn, tietoturvaan, käytettävyyteen, ylläpidettävyyteen jne.*

### 3.1 Auditointiloki (Audit Log)

Järjestelmään toteutetaan auditointiloki-toiminnallisuus, joka tallentaa tiedot käyttäjien tekemistä merkittävistä muutoksista järjestelmän tietoihin. Tämän tarkoituksena on parantaa järjestelmän läpinäkyvyyttä, jäljitettävyyttä ja luotettavuutta.

*   **Tallennettavat tiedot:** Lokiin kirjataan vähintään seuraavat tiedot kustakin merkittävästä muutostapahtumasta:
    *   Muutoksen tehnyt käyttäjä (`User`).
    *   Muutoksen tarkka ajankohta (timestamp).
    *   Muutoksen kohde (esim. viittaus muutettuun `Arviointi`-objektiin, `Hakemus`-objektiin tai muuhun relevanttiin tietueeseen).
    *   Tehty toimenpide (esim. 'LUONTI', 'MUOKKAUS', 'POISTO').
    *   Muutetut kentät ja niiden arvot (sekä vanha että uusi arvo, jos mahdollista ja tarkoituksenmukaista).
*   **Seurattavat kohteet:** Erityisen tärkeää on seurata muutoksia, jotka liittyvät:
    *   Arviointeihin (`Arviointi`-objektit): pisteiden (`pisteet`) ja kommenttien (`kommentti`) antaminen ja muokkaaminen.
    *   Hakemusten tiloihin (`Hakemus.tila`).
    *   Kampanja- ja haasteasetuksiin, jotka vaikuttavat arviointiprosessiin (esim. `Haaste.tila`, `Haaste.nayta_pisteet_arvioinnin_aikana`).
    *   Käyttäjärooleihin (`KampanjaKayttaja`, `HaasteKayttaja`).
*   **Käyttöliittymä:** Valtuutetuilla ylläpitäjillä tulee olla pääsy lokitietoihin käyttöliittymän kautta. Näkymän tulee mahdollistaa lokitietojen selaaminen ja suodattaminen esimerkiksi käyttäjän, ajankohdan tai muutoksen kohteen perusteella.
*   **Säilytys:** Lokitietojen säilytysaika määritellään erikseen (esim. tietosuojakäytäntöjen mukaisesti).

## 4. Arkkitehtuuri

*Kuvaa suunniteltu tekninen arkkitehtuuri, mukaan lukien backend, frontend, tietokanta ja muut keskeiset komponentit tai muutokset versiosta 1.0.*

Ehdotettu arkkitehtuuri perustuu moderneihin ja skaalautuviin teknologioihin, jotka tukevat järjestelmän joustavuutta, ylläpidettävyyttä ja laajennettavuutta.

*   **Backend (taustajärjestelmä):**
    *   Tarvitaan vankka **web-ohjelmistokehys (framework)**, joka tarjoaa hyvän tietokantatuen (ORM) ja mahdollisuuden toteuttaa ylläpitäjän käyttöliittymä tehokkaasti.
    *   Kehyksen päälle toteutetaan standardoitu **REST API -kerros**, joka toimii rajapintana frontendin ja mahdollisten ulkoisten integraatioiden kanssa.
    *   Tarvittaessa voidaan hyödyntää erillistä **asynkronisten tehtävien käsittelyjärjestelmää** pidempikestoisiin operaatioihin, kuten raportointiin tai ilmoitusten lähetykseen.
    *   Mahdollisia teknologioita näiden toteuttamiseen ovat esimerkiksi Python-pohjaiset kehykset kuten Django (Django REST Frameworkin ja Celeryn kanssa).

*   **Frontend (käyttöliittymä):**
    *   **Arvioijan käyttöliittymä:** Moderni JavaScript-framework, kuten React, Vue tai Svelte. Nämä mahdollistavat interaktiivisen ja dynaamisen käyttökokemuksen arvioijille, joka kommunikoi backendin kanssa REST API:n kautta.
    *   **Ylläpitäjän käyttöliittymä:** Hyödynnetään ensisijaisesti valitun backend-kehyksen tarjoamia ylläpitotoimintoja, joita voidaan tarvittaessa laajentaa ja kustomoida.

*   **Tietokanta:**
    *   PostgreSQL. Tehokas, luotettava ja avoimen lähdekoodin relaatiotietokanta, jolla on erinomainen tuki yleisimmille backend-kehysille, JSON-tietotyypeille ja skaalautuvuudelle.

*   **Tiedostojen tallennus:**
    *   Hakemusten liitetiedostot tallennetaan erilliseen tallennusratkaisuun. Kehitysvaiheessa ja pienemmissä asennuksissa tämä voi olla paikallinen tiedostojärjestelmä. Suuremmissa tai SaaS-ympäristöissä suositellaan pilvitallennusta (esim. AWS S3, Google Cloud Storage) skaalautuvuuden ja luotettavuuden varmistamiseksi.

*   **Auditointiloki:**
    *   Toteutetaan käyttäen joko valmista kirjastoa valitulle backend-kehykselle tai omalla toteutuksella, joka kirjaa muutokset tietokantaan tai erilliseen lokijärjestelmään.

Tämä arkkitehtuuri erottaa selvästi käyttöliittymälogiikan ja datanhallinnan, mikä helpottaa kehitystä ja ylläpitoa. REST API toimii keskeisenä rajapintana eri osien välillä.

## 5. Tietomalli

*Kuvaa tietokantaskeeman.*

### Kampanja (Campaign)

HUOM: muutetaan tämän objektityypin nimeksi "Haastekierros"

Kampanja edustaa ylätason arviointikierrosta tai -projektia (esim. tietty rahoitushaku, kilpailutus), jonka jokin taho (organisaatio, projekti) järjestää. Kampanja kokoaa yhteen yhteen tai useamman Haasteen (Challenge) ja hallinnoi yleisiä asetuksia sekä käyttäjärooleja kyseiselle kierrokselle. Kampanja luodaan aina uutena järjestelmään.

**Tietokentät:**

*   `nimi` (CharField): Kampanjan yksilöivä nimi (esim. "AI4Cities Rahoitushaku 2025").
*   `kuvaus` (TextField, valinnainen): Tarkempi kuvaus kampanjasta.
*   `jarjestaja_taho` (CharField): Kampanjan järjestävän tahon nimi (voi olla organisaatio, projekti tms.). *Huom: Harkitaan myöhemmin, tarvitaanko tähän erillinen `Organisaatio`-objekti.*
*   `alkamisaika` (DateTimeField, valinnainen): Kampanjan alkamisaika.
*   `paattymisaika` (DateTimeField, valinnainen): Kampanjan päättymisaika.
*   `tila` (CharField, choices): Kampanjan tila (esim. Suunnitteilla, Avoinna hakemuksille, Arvioinnissa, Päättynyt, Arkistoitu).
*   `ulkoasu_kustomointi` (JSONField/TextField, valinnainen): Mahdollistaa kampanjakohtaisen ulkoasun määrittelyn (esim. CSS). Toteutus avoin.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.
*   `omistaja_kayttaja` (ForeignKey -> User): Viittaus käyttäjään, joka loi kampanjan ja hallinnoi sitä ensisijaisesti.
*   `salli_keskustelut` (BooleanField, default=False): Määrittää, onko hakemuksiin liittyvä keskustelu oletusarvoisesti sallittu tämän kampanjan kaikissa haasteissa.

**Suhteet muihin objekteihin:**

*   **Haaste (Challenge):** Yksi kampanja sisältää yhden tai monta haastetta (OneToMany `Kampanja` -> `Haaste`).
*   **Käyttäjä (User):** Monta käyttäjää voi olla liitettynä kampanjaan eri rooleissa (ManyToMany `Kampanja` <-> `User` kautta esim. `KampanjaKayttaja`-välikappalemallin, joka määrittelee roolin kuten 'admin', 'arvioija').
    *   Kampanja-adminit voivat hallinnoida kampanjan asetuksia ja haasteita.
    *   Arvioijat voidaan liittää koko kampanjaan tai tarkemmin yksittäisiin haasteisiin (käsitellään `Haaste`-objektin yhteydessä).

**Toiminnallisuus:**

*   Käyttäjäroolien hallinta: Mahdollisuus määritellä kampanjalle admin-oikeudet omaavia käyttäjiä omistajan lisäksi.

**Avoimia kysymyksiä:**

*   Tarvitaanko `jarjestaja_taho`-kentän sijaan/lisäksi erillinen `Organisaatio`-objekti? (Tämä on erittäin nice to have, mutta ei välttämätöntä ainakaan tällä hetkellä).
*   Miten ulkoasun kustomointi tarkalleen toteutetaan ja periytyy/vaikuttaa haasteisiin?

### Haaste (Challenge)

Haaste edustaa spesifistä arviointikokonaisuutta Kampanjan sisällä, johon kohdistuu tietty joukko arviointikriteereitä ja johon liitetään arvioitavat hakemukset tai tarjoukset. Yksi Kampanja voi sisältää useita Haasteita. Haaste voidaan kloonata Kampanjan sisällä, mikä helpottaa uusien, samankaltaisten haasteiden luomista (esim. oletuskriteerien kopiointi).

**Tietokentät (ehdotus):**

*   `nimi` (CharField): Haasteen yksilöivä nimi kampanjan sisällä (esim. "Ratkaisut liikenteen päästövähennykseen").
*   `kuvaus` (TextField, valinnainen): Tarkempi kuvaus haasteesta.
*   `kampanja` (ForeignKey -> Kampanja, on_delete=models.CASCADE, related_name="haasteet"): Viittaus Kampanjaan, johon haaste kuuluu.
*   `hakemusten_alkamisaika` (DateTimeField, valinnainen): Aika, jolloin hakemusten jättäminen alkaa.
*   `hakemusten_paattymisaika` (DateTimeField, valinnainen): Aika, jolloin hakemusten jättäminen päättyy.
*   `arvioinnin_alkamisaika` (DateTimeField, valinnainen): Aika, jolloin arviointi alkaa.
*   `arvioinnin_paattymisaika` (DateTimeField, valinnainen): Aika, jolloin arviointi päättyy.
*   `tila` (CharField, choices): Haasteen tila (esim. Valmistelussa, Avoinna hakemuksille, Hakemukset arvioitavana, Arviointi päättynyt, Suljettu).
*   `kloonattu_haasteesta` (ForeignKey -> Haaste, null=True, blank=True, on_delete=models.SET_NULL, related_name="kloonit"): Viittaus alkuperäiseen haasteeseen, jos tämä haaste on klooni.
*   `nayta_pisteet_arvioinnin_aikana` (BooleanField, default=False): Määrittää, näkevätkö arvioijat toistensa antamat pisteet arvioinnin ollessa kesken.
*   `nayta_kommentit_arvioinnin_aikana` (BooleanField, default=False): Määrittää, näkevätkö arvioijat toistensa antamat kommentit arvioinnin ollessa kesken.
*   `salli_keskustelut` (BooleanField, null=True, blank=True, default=None): Määrittää, onko hakemuksiin liittyvä keskustelu sallittu tässä haasteessa. `None` perii asetuksen kampanjalta, `True` sallii, `False` kieltää.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.

**Suhteet muihin objekteihin:**

*   **Kampanja (Campaign):** Monta haastetta kuuluu yhteen kampanjaan (ManyToOne `Haaste` -> `Kampanja`).
*   **Hakemus (Application/Proposal):** Yksi haaste sisältää monta hakemusta (OneToMany `Haaste` -> `Hakemus`). *Huom: `Hakemus`-objekti määritellään myöhemmin.*
*   **Arviointikriteeri (EvaluationCriterion):** Yksi haaste sisältää monta arviointikriteeriä (tai kriteeriryhmää) (OneToMany `Haaste` -> `Arviointikriteeri`). *Huom: `Arviointikriteeri`-objekti ja sen rakenne (mahdolliset ryhmät) määritellään myöhemmin.*
*   **Käyttäjä (User):** Monta käyttäjää (arvioijaa, haasteen adminia) voidaan liittää haasteeseen (ManyToMany `Haaste` <-> `User` kautta esim. `HaasteKayttaja`-välikappalemallin, joka määrittelee roolin).
    *   Haaste-adminit voivat hallinnoida haasteen asetuksia (esim. aikoja, tilaa) ja arvioijia.
    *   Arvioijat arvioivat haasteeseen liitettyjä hakemuksia määriteltyjen kriteerien mukaisesti.

**Toiminnallisuus:**

*   Haasteen kloonaus kampanjan sisällä (kopioi asetukset ja mahdollisesti kriteeristön).
*   Arviointikriteerien määrittely ja hallinta haastekohtaisesti.
*   Arvioijien ja haaste-adminien liittäminen haasteeseen.
*   Mahdollisuus ladata haasteeseen liittyvät hakemukset (tiedostot ja/tai data).

**Avoimia kysymyksiä:**

*   Miten arviointikriteerien rakenne (yksi taso, monta tasoa, ryhmät) tarkalleen mallinnetaan ja liitetään haasteeseen? (Ks. suunnittelumuistion pohdinta eri projektien tarpeista).
*   Tarvitaanko tarkempaa tilanhallintaa (esim. erilliset tilat hakemusten vastaanotolle ja arvioinnille)? (Lisätty ehdotukseen).
*   Miten haastekohtaiset admin-roolit ja kampanja-admin-roolit eroavat oikeuksiltaan?

### Arviointikriteeri (EvaluationCriterion)

Arviointikriteeri edustaa joko arvioinnin osa-aluetta (ryhmää) tai konkreettista mittaria (kriteeriä), jolle annetaan pisteet hakemuksia arvioitaessa. Kriteerit ja ryhmät muodostavat hierarkkisen rakenteen Haasteen sisällä, mahdollistaen monimutkaistenkin arviointimallien määrittelyn (esim. pääryhmä -> alaryhmä -> kriteeri).

**Tietokentät (ehdotus):**

*   `haaste` (ForeignKey -> Haaste, on_delete=models.CASCADE, related_name="kriteeristö"): Viittaus Haasteeseen, johon kriteeri/ryhmä kuuluu.
*   `nimi` (CharField): Kriteerin tai ryhmän nimi (esim. "FR1.1 Challenge Fit", "Functional Requirements (FR)").
*   `koodi` (CharField, valinnainen): Kriteerin tai ryhmän koodi (esim. "FR1.1").
*   `lyhenne` (CharField, valinnainen): Kriteerin tai ryhmän lyhenne (esim. "C-FIT"). Tämä ehkä voidaan hoitaa yhdellä `koodi`-kentällä.
*   `kuvaus` (TextField, valinnainen): Tarkempi kuvaus kriteeristä tai ryhmästä.
*   `tyyppi` (CharField, choices=['RYHMÄ', 'KRITEERI']): Määrittää, onko kyseessä ryhmä (joka sisältää muita kriteereitä/ryhmiä) vai pisteillä arvioitava kriteeri.
*   `parent` (ForeignKey -> 'self', null=True, blank=True, on_delete=models.CASCADE, related_name="children"): Viittaus ylempään tasoon hierarkiassa (toiseen `Arviointikriteeri`-objektiin, jonka `tyyppi` on 'RYHMÄ'). Juuritason elementeillä tämä on `NULL`.
*   `painokerroin` (DecimalField, valinnainen): Kriteerin tai ryhmän painoarvo kokonaispisteitä laskettaessa. Miten painokertoimet tarkalleen toimivat hierarkiassa, pitää määritellä tarkemmin.
*   `maksimipisteet` (IntegerField, valinnainen): Suurin mahdollinen pistemäärä, joka voidaan antaa `KRITEERI`-tyyppiselle objektille.
*   `kynnysarvo` (IntegerField, valinnainen): Pistemäärä, joka `KRITEERI`-tyyppisen objektin on vähintään saavutettava (jos määritelty). Alitus voi johtaa hakemuksen hylkäämiseen.
*   `järjestysnumero` (IntegerField, default=0): Määrittää kriteerien/ryhmien järjestyksen saman `parent`-elementin alla.
*   `admin_vain` (BooleanField, default=False): Jos `True`, vain kampanja- ja haaste-adminit näkevät ja voivat asettaa arvon (`Arviointi`-objektin) tälle kriteerille. Hyödyllinen esim. hinta-kriteereille, joiden arvo lasketaan ulkoisesti ja syötetään järjestelmään adminin toimesta.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.

**Suhteet muihin objekteihin:**

*   **Haaste (Challenge):** Monta kriteeriä/ryhmää kuuluu yhteen haasteeseen (ManyToOne `Arviointikriteeri` -> `Haaste`).
*   **Arviointikriteeri (EvaluationCriterion):** Monta kriteeriä/ryhmää voi kuulua yhteen ylempään ryhmään (ManyToOne `Arviointikriteeri` -> `Arviointikriteeri` [`parent`]). Yksi ryhmä voi sisältää monta alikriteeriä/ryhmää (OneToMany `Arviointikriteeri` -> `Arviointikriteeri` [`children`]).
*   **Arviointi (Evaluation/Score):** Arvioijat antavat pisteitä ja kommentteja `KRITEERI`-tyyppisille objekteille liittyen. Tämä yhteys todennäköisesti toteutetaan erillisellä `Arviointi`-objektilla (määritellään myöhemmin), joka viittaa `Hakemukseen`, `Arviointikriteeriin` ja `Arvioijaan`.
*   **KriteeriArvioija (CriterionEvaluatorAssignment):** Yksi kriteeri voi olla liitettynä useaan `KriteeriArvioija`-tietueeseen (OneToMany `Arviointikriteeri` -> `KriteeriArvioija`). *Nice-to-have.*

**Toiminnallisuus:**

*   Mahdollistaa monitasoisen kriteerihierarkian luomisen haastekohtaisesti.
*   Sallii painokertoimien, maksimipisteiden ja kynnysarvojen määrittelyn.
*   Määrittää rakenteen, johon arvioinnit (pisteet, kommentit) voidaan liittää.
*   Mahdollistaa tiettyjen kriteerien rajaamisen vain admin-käyttäjille (`admin_vain`).
*   Mahdollistaa kriteerien kohdentamisen tietyille arvioijille (`KriteeriArvioija`-mallin kautta).

**Avoimia kysymyksiä:**

*   Miten painokertoimet lasketaan ja vaikuttavat hierarkian eri tasoilla? Periikö aliryhmä/kriteeri yläryhmän painokertoimen vai lasketaanko painotus suhteessa sisaruksiin? (Tärkeä määrittely laskentalogiikkaa varten).
*   Miten kommentointi tarkalleen toimii? Voiko kommentteja liittää myös 'RYHMÄ'-tyyppisille objekteihin, kuten vanhassa mallissa mainittiin? (Todennäköisesti kyllä, `Arviointi`-objektin kautta).
*   Tarvitaanko lisäkenttiä ohjeistamaan arvioijaa kriteerin osalta?
*   Miten varmistetaan, että vain `KRITEERI`-tyyppisillä objekteilla on `maksimipisteet` ja `kynnysarvo`? (Voidaan validoida mallin tasolla).
*   Miten varmistetaan, että `admin_vain`-kriteereille voivat luoda `Arviointi`-objekteja vain käyttäjät, joilla on admin-rooli kyseisessä haasteessa tai kampanjassa?

### Arviointi (Evaluation/Score)

Arviointi edustaa yhden arvioijan antamaa pistemäärää ja/tai kommenttia yhdelle hakemukselle tietyn arviointikriteerin osalta. Jokaista hakemuksen ja arviointikriteerin paria kohden yksi arvioija voi luoda vain yhden arviointiobjektin.

**Tietokentät (ehdotus):**

*   `hakemus` (ForeignKey -> Hakemus, on_delete=models.CASCADE, related_name="arvioinnit"): Viittaus arvioitavaan Hakemukseen. *Huom: `Hakemus`-objekti määritellään myöhemmin.*
*   `kriteeri` (ForeignKey -> Arviointikriteeri, on_delete=models.CASCADE, related_name="arvioinnit"): Viittaus Arviointikriteeriin, johon tämä arviointi liittyy. Tämän kriteerin `tyyppi` on oltava 'KRITEERI'.
*   `arvioija` (ForeignKey -> User, on_delete=models.PROTECT, related_name="arvioinnit"): Viittaus arvioinnin tehneeseen käyttäjään.
*   `pisteet` (IntegerField, null=True, blank=True): Arvioijan antama numeerinen pistemäärä. Arvo on `NULL`, jos arvioija ei ole vielä antanut pisteitä tai jos kriteeri ei vaadi pisteitä (vaikka yleensä vaatii). Validoidaan `kriteeri.maksimipisteet` -arvoa vastaan.
*   `kommentti` (TextField, null=True, blank=True): Arvioijan antama sanallinen kommentti tai perustelu pisteille.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.

**Suhteet muihin objekteihin:**

*   **Hakemus (Application/Tender/Proposal/Offer):** Monta arviointia liittyy yhteen hakemukseen (ManyToOne `Arviointi` -> `Hakemus`).
*   **Arviointikriteeri (EvaluationCriterion):** Monta arviointia liittyy yhteen kriteeriin (ManyToOne `Arviointi` -> `Arviointikriteeri`).
*   **Käyttäjä (User):** Monta arviointia liittyy yhteen käyttäjään (arvioijaan) (ManyToOne `Arviointi` -> `User`).

**Toiminnallisuus:**

*   Tallentaa yksittäisen arvioijan näkemyksen hakemuksesta tietyn kriteerin osalta.
*   Mahdollistaa pisteiden ja/tai kommenttien antamisen.
*   Toimii perustana kokonaispisteiden laskennalle ja arviointien yhteenvedoille.
*   Arvioinnin näkyvyyttä muiden arvioijien kesken hallitaan `Haaste`-objektin `nayta_pisteet_arvioinnin_aikana` ja `nayta_kommentit_arvioinnin_aikana` -kenttien kautta.

**Avoimia kysymyksiä:**

*   Miten käsitellään tilanne, jos arviointikriteeriä muokataan (esim. `maksimipisteet` muuttuu) sen jälkeen, kun arviointeja on jo annettu? (Vaatii validointia/logiikkaa).
*   Tarvitaanko erillinen tila arvioinnille (esim. 'Luonnos', 'Valmis')? (Mahdollisesti hyödyllinen).
*   Miten mahdolliset kynnysarvon (`kriteeri.kynnysarvo`) alitukset merkitään tai raportoidaan?
*   Pitäisikö kommentointi olla mahdollista myös 'RYHMÄ'-tyyppisille kriteereille, kuten vanhassa mallissa mainittiin? Jos kyllä, pitäisikö `kriteeri`-kentän viitata myös ryhmiin, ja miten `pisteet` tällöin käsitellään? (Tämä lisäisi kompleksisuutta, harkitaan tarkkaan tarvetta).

### Hakemus (Application/Tender/Proposal/Offer)

Hakemus edustaa Haasteeseen jätettyä ehdotusta, tarjousta tai muuta vastaavaa dokumenttikokonaisuutta, joka arvioidaan määriteltyjen kriteerien mukaisesti.

**Tietokentät (ehdotus):**

*   `haaste` (ForeignKey -> Haaste, on_delete=models.CASCADE, related_name="hakemukset"): Viittaus Haasteeseen, johon hakemus kuuluu.
*   `otsikko` (CharField): Hakemuksen otsikko tai nimi.
*   `tiivistelmä` (TextField, valinnainen): Lyhyt kuvaus tai tiivistelmä hakemuksesta.
*   `hakija_nimi` (CharField): Hakemuksen jättäneen tahon (henkilö, tiimi, organisaatio) nimi.
*   `hakija_email` (EmailField, valinnainen): Hakijan sähköpostiosoite yhteydenottoa varten.
*   `hakija_lisätiedot` (JSONField/TextField, valinnainen): Muita hakijaan liittyviä tietoja strukturoidussa tai vapaamuotoisessa muodossa (esim. puhelinnumero, organisaation y-tunnus).
*   `sisältö_data` (JSONField/TextField, valinnainen): Hakemuksen strukturoitu sisältö, jos se ei ole pelkästään liitetiedostoissa (esim. vastaukset kysymyslomakkeeseen).
*   `tila` (CharField, choices): Hakemuksen tila (esim. Luonnos, Lähetetty, Arvioinnissa, Vaatii lisätietoja, Hyväksytty, Hylätty).
*   `lähetysaika` (DateTimeField, null=True, blank=True): Aika, jolloin hakemus virallisesti lähetettiin.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.
*   `jättäjä_käyttäjä` (ForeignKey -> User, null=True, blank=True, on_delete=models.SET_NULL, related_name="jätetyt_hakemukset"): Viittaus järjestelmän käyttäjään, joka jätti hakemuksen (jos relevantti ja mahdollista).
*   `vastuu_admin` (ForeignKey -> User, null=True, blank=True, on_delete=models.SET_NULL, related_name="vastuuhakemukset"): Viittaus järjestelmän käyttäjään (todennäköisesti kampanja- tai haasteadmin), joka toimii ensisijaisena yhteyshenkilönä tai vastuuhenkilönä tälle hakemukselle järjestäjän puolelta.

**Suhteet muihin objekteihin:**

*   **Haaste (Challenge):** Monta hakemusta kuuluu yhteen haasteeseen (ManyToOne `Hakemus` -> `Haaste`).
*   **Arviointi (Evaluation/Score):** Yksi hakemus saa monta arviointia (yksi per arvioija per kriteeri) (OneToMany `Hakemus` -> `Arviointi`).
*   **Liitetiedosto (Attachment):** Yksi hakemus voi sisältää monta liitetiedostoa (OneToMany `Hakemus` -> `Liitetiedosto`). *Huom: `Liitetiedosto`-objekti määritellään erikseen.*
*   **Käyttäjä (User):** Yksi käyttäjä voi jättää monta hakemusta (jos `jättäjä_käyttäjä`-kenttää käytetään).

**Toiminnallisuus:**

*   Tallentaa hakemuksen perustiedot ja sisällön (tai viittaukset siihen).
*   Seuraa hakemuksen tilaa sen elinkaaren ajan.
*   Linkittää hakemuksen oikeaan haasteeseen ja mahdollistaa sen arvioinnin.

**Avoimia kysymyksiä:**

*   Miten hallitaan tilannetta, jossa hakemuksen voi jättää sekä rekisteröitynyt käyttäjä että ulkopuolinen taho? Onko `jättäjä_käyttäjä` ja `hakija_*`-kentät riittävä yhdistelmä?
*   Tarvitaanko tarkempia kenttiä hakemuksen sisältöön liittyen (esim. budjetti, avainsanat) vai riittääkö `sisältö_data` ja liitteet?
*   Miten hakemuspohjia tai -lomakkeita hallitaan ja linkitetään haasteeseen? (Tämä voi olla osa Haasteen määrittelyä).
*   **Hakemuksen siirtyminen haasteiden välillä:** Miten mallinnetaan ja hallitaan tilanne, jossa hakemus voi siirtyä haasteesta toiseen (esim. esikarsinnasta jatkoarviointiin)?
    *   Vaikka arvioinnit säilyvät, tarvitaanko erillinen mekanismi (kuten `HakemusHistoria`-malli) seuraamaan, missä haasteessa hakemus on ollut milloinkin?
    *   Miten varmistetaan, että arvioijalle näytetään oikeat ja relevantit hakemuksen tiedot kussakin arviointivaiheessa (haasteessa)? Esimerkiksi esikarsinnassa voidaan näyttää vain tiivistelmä, kun taas jatkoarvioinnissa kaikki tiedot ja liitteet. Pitääkö `Hakemus`-mallia laajentaa vai riittääkö käyttöliittymälogiikka ohjaamaan näytettävää dataa `Haaste`-kontekstin perusteella? Vai kannattaisiko Hakemuksesta tallentaa uusi versio jokaiseen arviointivaiheeseen? (Tämä vaatii tarkempaa suunnittelua, koska Application ID olisi eri haasteissa sama.)

### Liitetiedosto (Attachment)

Liitetiedosto edustaa yksittäistä tiedostoa, joka on liitetty Hakemukseen. Yksi hakemus voi sisältää useita liitetiedostoja.

**Tietokentät (ehdotus):**

*   `hakemus` (ForeignKey -> Hakemus, on_delete=models.CASCADE, related_name="liitetiedostot"): Viittaus Hakemukseen, johon liitetiedosto kuuluu.
*   `tiedosto` (FileField): Viittaus tallennettuun tiedostoon (esim. Django `FileField` tai vastaava, joka hallinnoi tallennusta).
*   `tiedostonimi` (CharField): Alkuperäinen tiedostonimi, jolla tiedosto ladattiin.
*   `tiedostotyyppi` (CharField): Tiedoston MIME-tyyppi (esim. 'application/pdf', 'image/jpeg'). Tämä auttaa käyttöliittymää näyttämään tiedoston oikein.
*   `koko` (IntegerField): Tiedoston koko tavuina.
*   `kuvaus` (TextField, valinnainen): Lyhyt kuvaus liitetiedoston sisällöstä.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima (milloin tietue luotiin).
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.

**Suhteet muihin objekteihin:**

*   **Hakemus (Application/Tender/Proposal/Offer):** Monta liitetiedostoa kuuluu yhteen hakemukseen (ManyToOne `Liitetiedosto` -> `Hakemus`).

**Toiminnallisuus:**

*   Tallentaa viittauksen tiedostoon ja sen keskeiset metatiedot (nimi, tyyppi, koko).
*   Mahdollistaa tiedostojen liittämisen hakemuksiin.

**Avoimia kysymyksiä:**

*   Missä ja miten tiedostot fyysisesti tallennetaan (esim. paikallinen tiedostojärjestelmä, pilvitallennus kuten S3)? Tämä vaikuttaa `tiedosto`-kentän toteutukseen.
*   Tarvitaanko tarkempia pääsynhallintasääntöjä liitetiedostoille (esim. kuka voi ladata/poistaa)?
*   Miten käsitellään tiedostojen versiointia, jos hakemusta päivitetään?

### HakemusViesti (ApplicationMessage)

HakemusViesti edustaa yksittäistä viestiä, joka on lähetetty tietyn hakemuksen yhteydessä käytävään keskusteluun. Keskustelun näkyvyys ja salliminen määritellään Kampanja- ja Haastetasolla.

**Tietokentät (ehdotus):**

*   `hakemus` (ForeignKey -> Hakemus, on_delete=models.CASCADE, related_name="viestit"): Viittaus Hakemukseen, johon viesti liittyy.
*   `kayttaja` (ForeignKey -> User, on_delete=models.SET_NULL, null=True, related_name="hakemusviestit"): Viittaus viestin lähettäneeseen käyttäjään. Jos käyttäjä poistetaan, viesti säilyy ilman lähettäjätietoa.
*   `viesti` (TextField): Viestin sisältö.
*   `created_at` (DateTimeField, auto_now_add): Viestin lähetysaika.
*   `parent` (ForeignKey -> 'self', null=True, blank=True, on_delete=models.CASCADE, related_name="vastaukset"): Viittaus alkuperäiseen viestiin, jos tämä on vastaus (mahdollistaa ketjutuksen). Juuriviesteillä tämä on `NULL`.

**Suhteet muihin objekteihin:**

*   **Hakemus (Application):** Monta viestiä liittyy yhteen hakemukseen (ManyToOne `HakemusViesti` -> `Hakemus`).
*   **Käyttäjä (User):** Yksi käyttäjä voi lähettää monta viestiä (ManyToOne `HakemusViesti` -> `User`).
*   **HakemusViesti (ApplicationMessage):** Yksi viesti voi saada monta vastausta (OneToMany `HakemusViesti` -> `HakemusViesti` [`vastaukset`]). Monta vastausta voi liittyä yhteen parent-viestiin (ManyToOne `HakemusViesti` -> `HakemusViesti` [`parent`]).

**Toiminnallisuus:**

*   Tallentaa hakemuskohtaisen keskustelun viestit.
*   Mahdollistaa ketjutettujen keskustelujen muodostamisen.
*   Keskustelun saatavuutta ja näkyvyyttä ohjataan `Kampanja.salli_keskustelut` ja `Haaste.salli_keskustelut` -kentillä.

**Avoimia kysymyksiä:**

*   Ketkä käyttäjät (mitkä roolit) tarkalleen voivat nähdä keskustelun ja lähettää viestejä kuhunkin hakemukseen? (Todennäköisesti ne, joilla on pääsy hakemukseen roolien perusteella).
*   Tarvitaanko viesteille muokkaus- tai poistotoimintoa? Jos kyllä, millä ehdoilla ja kenen toimesta?
*   Miten uusista viesteistä ilmoitetaan käyttäjille (esim. sähköposti-ilmoitukset)?

### Kampanjan Käyttäjä (CampaignUser)

Tämä välikappalemalli yhdistää Käyttäjän (User) tiettyyn Kampanjaan ja määrittää käyttäjän roolin kyseisessä kampanjassa.

**Tietokentät (ehdotus):**

*   `kampanja` (ForeignKey -> Kampanja, on_delete=models.CASCADE, related_name="kayttajat"): Viittaus Kampanjaan.
*   `kayttaja` (ForeignKey -> User, on_delete=models.CASCADE, related_name="kampanja_roolit"): Viittaus Käyttäjään.
*   `rooli` (CharField, choices=['admin', 'arvioija']): Käyttäjän rooli kampanjassa. *Huom: Roolivaihtoehtoja voidaan laajentaa tarvittaessa.*
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.

**Rajoitteet:**

*   Yksi käyttäjä voi olla liitettynä yhteen kampanjaan vain yhdellä roolilla (`unique_together = ('kampanja', 'kayttaja')`). Jos käyttäjällä on useita rooleja, ne on käsiteltävä sovelluslogiikassa tai roolimallia laajentamalla.

**Suhteet muihin objekteihin:**

*   Linkittää `Kampanja`- ja `User`-objektit (ManyToMany-suhteen toteutus).

**Toiminnallisuus:**

*   Määrittää kampanjakohtaiset oikeudet (admin, arvioija).
*   Mahdollistaa käyttäjien hallinnan kampanjatasolla. Kampanja-adminit voivat lisätä/poistaa muita admineita ja arvioijia kampanjaan.
*   Kampanjaan 'arvioija'-roolilla liitetyt käyttäjät voivat oletusarvoisesti nähdä ja arvioida kaikkia kampanjan haasteita ja niiden hakemuksia, ellei `HaasteKayttaja`-tasolla ole tarkempia määrityksiä.

**Avoimia kysymyksiä:**

*   Tarvitaanko tarkempia rooleja kampanjatasolla?
*   Miten varmistetaan, että kampanjalla on aina vähintään yksi admin (esim. `omistaja_kayttaja` automaattisesti admin-roolilla)?

### Haasteen Käyttäjä (ChallengeUser)

Tämä välikappalemalli yhdistää Käyttäjän (User) tiettyyn Haasteeseen ja määrittää käyttäjän roolin kyseisessä haasteessa. Tämä mahdollistaa tarkemman oikeuksien hallinnan kuin pelkkä kampanjatason rooli.

**Tietokentät (ehdotus):**

*   `haaste` (ForeignKey -> Haaste, on_delete=models.CASCADE, related_name="kayttajat"): Viittaus Haasteeseen.
*   `kayttaja` (ForeignKey -> User, on_delete=models.CASCADE, related_name="haaste_roolit"): Viittaus Käyttäjään.
*   `rooli` (CharField, choices=['admin', 'arvioija']): Käyttäjän rooli haasteessa. *Huom: Roolivaihtoehtoja voidaan laajentaa tarvittaessa.*
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.

**Rajoitteet:**

*   Yksi käyttäjä voi olla liitettynä yhteen haasteeseen vain yhdellä roolilla (`unique_together = ('haaste', 'kayttaja')`).

**Suhteet muihin objekteihin:**

*   Linkittää `Haaste`- ja `User`-objektit (ManyToMany-suhteen toteutus).

**Toiminnallisuus:**

*   Määrittää haastekohtaiset oikeudet (admin, arvioija).
*   Haaste-adminit voivat hallinnoida haasteen asetuksia ja lisätä/poistaa arvioijia *kyseiseen* haasteeseen.
*   Jos käyttäjä on määritelty arvioijaksi `HaasteKayttaja`-tasolla, hän voi arvioida vain kyseisen haasteen hakemuksia, vaikka hänellä olisi laajempi 'arvioija'-rooli `KampanjaKayttaja`-tasolla. Tämä mahdollistaa arvioijien kohdentamisen tiettyihin haasteisiin.
*   Jos käyttäjää ei ole erikseen liitetty haasteeseen `HaasteKayttaja`-mallilla, mutta hänellä on 'arvioija'-rooli kampanjatasolla (`KampanjaKayttaja`), hän voi oletusarvoisesti arvioida haasteen hakemuksia (pois lukien `admin_vain`-kriteerit).
*   *(Nice-to-have):* Jos `KriteeriArvioija`-määrityksiä on tehty tälle käyttäjälle tässä haasteessa, hän voi arvioida vain ne kriteerit, jotka hänelle on erikseen määritelty.

**Avoimia kysymyksiä:**

*   Tarvitaanko tarkempia rooleja haastetasolla?
*   Miten haastekohtaisten ja kampanjatason roolien vuorovaikutus ja oikeuksien periytyminen tarkalleen toteutetaan ja validoidaan? (Peruslogiikka kuvattu toiminnallisuudessa, mutta vaatii tarkempaa suunnittelua).
*   *(Nice-to-have):* Miten `KriteeriArvioija`-määritysten hallinta toteutetaan ylläpitäjän käyttöliittymässä?

<harkittava poistettavaksi>
### Organisaatio (Organisation)

Nice to have.

Organisaatio edustaa tahoa (yritys, julkinen toimija, projekti tms.), joka voi järjestää Kampanjoita tai johon käyttäjät voivat kuulua.

**Tietokentät (ehdotus):**

*   `nimi` (CharField, unique=True): Organisaation täydellinen nimi.
*   `lyhenne` (CharField, unique=True, null=True, blank=True, db_index=True): Organisaation lyhenne tai koodi.
*   `kuvaus` (TextField, null=True, blank=True): Vapaamuotoinen kuvaus organisaatiosta.
*   `verkkosivusto` (URLField, null=True, blank=True): Organisaation verkkosivun osoite.
*   `created_at` (DateTimeField, auto_now_add): Luoja-aikaleima.
*   `modified_at` (DateTimeField, auto_now): Muokkausaikaleima.

**Suhteet muihin objekteihin:**

*   **Kampanja (Campaign):** Yksi organisaatio voi järjestää monta kampanjaa (OneToMany `Organisaatio` -> `Kampanja`).
*   **Käyttäjä (User):** Monta käyttäjää voi kuulua yhteen organisaatioon ja yksi käyttäjä voi kuulua moneen organisaatioon (ManyToMany `Organisaatio` <-> `User` kautta `OrganisaatioKayttaja`-välimallin).

**Toiminnallisuus:**

*   Tarjoaa keskitetyn paikan organisaatiotietojen hallintaan.
*   Mahdollistaa kampanjoiden liittämisen tiettyyn järjestäjään.
*   Mahdollistaa käyttäjien liittämisen organisaatioihin.

**Avoimia kysymyksiä:**

*   Tarvitaanko tarkempia rooleja tai tietoja käyttäjän ja organisaation väliseen suhteeseen (`OrganisaatioKayttaja`)? (Tässä vaiheessa oletetaan pelkkä jäsenyys).
*   Kuka hallinnoi organisaatiotietoja? (Todennäköisesti ylläpitäjät).
</harkittava poistettavaksi>

<harkittava poistettavaksi>
### Organisaation käyttäjä (OrganisationUser)

Tämä välikappalemalli yhdistää Käyttäjän (User) tiettyyn Organisaatioon.

**Tietokentät (ehdotus):**

*   `organisaatio` (ForeignKey -> Organisaatio, on_delete=models.CASCADE, related_name="kayttajat"): Viittaus Organisaatioon.
*   `kayttaja` (ForeignKey -> User, on_delete=models.CASCADE, related_name="organisaatio_jasenyydet"): Viittaus Käyttäjään.
*   `created_at` (DateTimeField, auto_now_add): Liittymisen aikaleima.

**Rajoitteet:**

*   Yksi käyttäjä voi olla liitettynä yhteen organisaatioon vain kerran (`unique_together = ('organisaatio', 'kayttaja')`).

**Suhteet muihin objekteihin:**

*   Linkittää `Organisaatio`- ja `User`-objektit (ManyToMany-suhteen toteutus).

**Toiminnallisuus:**

*   Mahdollistaa käyttäjien liittämisen organisaatioihin.
*   Voidaan tulevaisuudessa laajentaa rooleilla tai muilla tiedoilla tarvittaessa.

**Avoimia kysymyksiä:**

*   Riittääkö pelkkä jäsenyys vai tarvitaanko rooleja tai muita tietoja? (Ks. `Organisaatio`-mallin avoimet kysymykset).

</harkittava poistettavaksi>

## 6. Käyttöliittymä (UI) / Käyttäjäkokemus (UX)

*Kuvaa merkittävät muutokset tai uudet suunnitelmat käyttöliittymälle.*

### 6.1. Ylläpitäjän käyttöliittymä (Admin UI)

Tässä osiossa kuvaillaan ylläpitäjän (admin) käyttöliittymän suunnitelma, hyödyntäen valitun taustajärjestelmän tarjoamia sisäänrakennettuja ylläpitotoimintoja mahdollisimman pitkälle. Ylläpitäjät koulutetaan käyttämään näitä toimintoja.

**Yleistä:**

*   Valtuutettujen ylläpitäjien (esim. `KampanjaKayttaja`-roolin 'admin' kautta) tulee pystyä hallinnoimaan kaikkia keskeisiä tietoja järjestelmässä.
*   Käyttöliittymän tulisi tarjota selkeät listanäkymät ja muokkausnäkymät kullekin tietorakenteelle.

**Kampanja (Campaign):**

*   **Listanäkymä:** Näyttää keskeiset tiedot, kuten `nimi`, `jarjestaja_taho`, `tila`, `alkamisaika`, `paattymisaika`. Mahdollistaa suodatuksen `tila`-kentän mukaan ja haun `nimi`-kentällä.
*   **Muokkausnäkymä:**
    *   Sallii kaikkien kampanjan kenttien muokkauksen (`nimi`, `kuvaus`, `jarjestaja_taho`, ajat, `tila` jne.).
    *   Tarjoaa tavan hallinnoida kampanjaan liittyviä käyttäjiä (`KampanjaKayttaja`): käyttäjien lisääminen/poistaminen ja roolien (`admin`, `arvioija`) määrittäminen. `omistaja_kayttaja` voisi olla vain luku -tyyppinen tai automaattisesti asetettu.
    *   Mahdollistaa `ulkoasu_kustomointi`-kentän muokkauksen (esim. tekstikenttä CSS/JSON-määrittelyille).
    *   Näyttää linkitetyt `Haaste`-objektit ja mahdollistaa siirtymisen niiden hallintaan.

**Haaste (Challenge):**

*   **Listanäkymä:** Usein käytettävissä `Kampanja`-näkymän kautta. Näyttää `nimi`, `tila` ja keskeiset päivämäärät (`hakemusten_*`, `arvioinnin_*`). Mahdollistaa suodatuksen `tila`-kentän mukaan.
*   **Muokkausnäkymä:**
    *   Sallii kaikkien haasteen kenttien muokkauksen.
    *   Tarjoaa tavan hallinnoida haasteeseen liittyviä käyttäjiä (`HaasteKayttaja`): arvioijien ja haaste-adminien lisääminen/poistaminen *tähän* haasteeseen.
    *   Tarjoaa tavan hallinnoida haasteen arviointikriteerejä (`Arviointikriteeri`), mukaan lukien hierarkian luomisen ja muokkaamisen.
    *   Sisältää toiminnallisuuden haasteen kloonaamiseksi kampanjan sisällä ("Kloonaa haaste").
    *   Näyttää linkin alkuperäiseen haasteeseen (`kloonattu_haasteesta`), jos kyseessä on klooni.
    *   Näyttää linkitetyt `Hakemus`-objektit ja mahdollistaa siirtymisen niiden hallintaan.

**Arviointikriteeri (EvaluationCriterion):**

*   **Hallinta:** Todennäköisesti upotettuna `Haaste`-muokkausnäkymään.
*   **Hierarkia:** Käyttöliittymän tulee tukea hierarkian (`parent`/`children`) luomista ja muokkaamista (esim. sisäkkäinen muokkaus, puunäkymä).
*   **Kentät:** `maksimipisteet` ja `kynnysarvo` tulee olla muokattavissa vain, kun `tyyppi` on 'KRITEERI'. `painokerroin`-kentän toimintalogiikka tulee selventää käyttöliittymässä (perustuen avoimeen kysymykseen spesifikaatiossa). Järjestystä (`järjestysnumero`) tulee voida muuttaa helposti (esim. raahaamalla tai nuolipainikkeilla).
*   **Rajoitukset:** Varmistetaan, että vain `KRITEERI`-tyyppisille kohteille voi antaa `maksimipisteet`.

**Hakemus (Application/Tender/Proposal/Offer):**

*   **Listanäkymä:** Usein käytettävissä `Haaste`-näkymän kautta. Näyttää `otsikko`, `hakija_nimi`, `tila`, `lähetysaika`. Mahdollistaa suodatuksen `tila`-kentän mukaan ja haun `otsikko` tai `hakija_nimi` -kentillä.
*   **Muokkausnäkymä:**
    *   Ylläpitäjä voi muokata lähinnä tilatietoja (`tila`) tai asettaa `vastuu_admin`:in. Hakijan tiedot (`hakija_*`, `sisältö_data`) ovat pääasiassa vain luku -muodossa.
    *   Näyttää liittyvät `Liitetiedosto`-objektit (latausmahdollisuus). Ylläpitäjä voi tarvittaessa poistaa tai lisätä liitteitä.
    *   Tarjoaa näkymän hakemukseen liittyviin arviointeihin (`Arviointi`), mahdollisesti yhteenvetona (esim. keskiarvot, arviointien tila per arvioija).
    *   Tarjoaa pääsyn hakemukseen liittyvään keskusteluun (`HakemusViesti`).

**Arviointi (Evaluation/Score):**

*   **Hallinta:** Ylläpitäjä ei yleensä luo tai muokkaa arviointeja suoraan.
*   **Näkymä:** Arvioinnit ovat nähtävissä `Hakemus`-näkymän kautta tai mahdollisesti omassa listanäkymässään, jossa voi suodattaa esim. `Arvioija`- tai `Hakemus`-tiedon perusteella. Ylläpitäjän tulee voida tarkastella yksittäisen arvioinnin tietoja (`pisteet`, `kommentti`) valvontaa tai ongelmanratkaisua varten.

**Liitetiedosto (Attachment):**

*   **Hallinta:** Pääasiassa `Hakemus`-muokkausnäkymän kautta.
*   **Toiminnot:** Mahdollistaa liitteiden tarkastelun (nimi, tyyppi, koko) ja lataamisen. Ylläpitäjä voi tarvittaessa poistaa liitteitä tai lisätä uusia.

**HakemusViesti (ApplicationMessage):**

*   **Hallinta:** Nähtävissä `Hakemus`-näkymän kautta, näyttäen viestiketjun rakenteen.
*   **Moderaatio:** Ylläpitäjillä tulisi olla mahdollisuus moderoida keskustelua tarvittaessa (esim. poistaa viestejä).

**KampanjaKayttaja (CampaignUser) & HaasteKayttaja (ChallengeUser):**

*   **Hallinta:** Käyttäjien ja roolien hallinta tapahtuu vastaavien `Kampanja`- ja `Haaste`-muokkausnäkymien kautta (inline-muokkaus).
*   **Käyttöliittymä:** Tarvitaan selkeä tapa valita käyttäjä (esim. pudotusvalikko tai haku) ja määrittää rooli ('admin'/'arvioija'). `HaasteKayttaja`-näkymässä käyttäjälista voitaisiin rajata kampanjan käyttäjiin.

**Käyttäjien hallinta (User Management):**

*   Taustajärjestelmän oletuskäyttäjähallintaa voidaan hyödyntää. Sitä voidaan laajentaa näyttämään, mihin kampanjoihin ja haasteisiin käyttäjä liittyy rooleineen.

### 6.2. Arvioijan Käyttöliittymä (Evaluator UI/UX)

Tässä luonnos arvioijan näkymistä ja toiminnoista, tavoitteena tehdä arviointiprosessista mahdollisimman sujuva ja intuitiivinen:

**1. Kojelauta / Etusivu (Dashboard/Homepage):**

*   **Tarkoitus:** Tarjota arvioijalle nopea yleiskatsaus hänen tehtävistään ja edistymisestään.
*   **Sisältö:**
    *   Lista kampanjoista ja haasteista, joihin arvioija on liitetty ja joissa on aktiivisia arviointitehtäviä (`Haaste.tila` = 'Hakemukset arvioitavana').
    *   Kullekin haasteelle näytetään:
        *   Haasteen nimi (`Haaste.nimi`).
        *   Arvioitavien hakemusten kokonaismäärä.
        *   Arvioijan itse arvioimien hakemusten määrä (ja/tai prosenttiosuus).
        *   Haasteen arvioinnin määräaika (`Haaste.arvioinnin_paattymisaika`), jos asetettu.
    *   Pikakuvakkeet/linkit siirtyä suoraan arvioimaan tietyn haasteen hakemuksia.
    *   Mahdollisesti ilmoitukset (esim. uudet viestit keskusteluissa, lähestyvät määräajat).

**2. Haasteen arviointinäkymä (Challenge evaluation view):**

*   **Tarkoitus:** Listata kaikki haasteeseen liittyvät hakemukset ja näyttää niiden arviointistatus.
*   **Sisältö:**
    *   Haasteen perustiedot (nimi, kuvaus).
    *   Lista haasteeseen saapuneista hakemuksista (`Hakemus`). Kullekin hakemukselle näytetään:
        *   Hakemuksen tunniste/otsikko (`Hakemus.otsikko`).
        *   Hakijan nimi (`Hakemus.hakija_nimi`).
        *   Arvioijan oma arviointistatus tälle hakemukselle (esim. "Aloittamatta", "Kesken", "Valmis"). Tilatieto voidaan päätellä `Arviointi`-objektien olemassaolosta ja tilasta (jos lisätään tilakenttä `Arviointi`-malliin).
        *   Mahdollisesti linkki hakemuksen keskusteluun (`HakemusViesti`), jos `salli_keskustelut` on tosi.
    *   **Suodatus ja Järjestely:** Mahdollisuus suodattaa hakemuksia oman arviointistatuksen mukaan (esim. näytä vain arvioimattomat) ja järjestää listaa (esim. hakijan nimen tai lähetysajan mukaan).
    *   Linkki siirtyä yksittäisen hakemuksen arviointinäkymään.

**3. Hakemuksen arviointinäkymä (Application evaluation view):**

*   **Tarkoitus:** Mahdollistaa yhden hakemuksen arviointi kriteerien perusteella. Tämä on arvioijan pääasiallinen työnäkymä.
*   **Layout:** Usein kaksipalstainen:
    *   **Vasen/Yläosa:** Hakemuksen tiedot ja liitteet.
        *   Hakemuksen perustiedot (`otsikko`, `tiivistelmä`, `hakija_*`).
        *   Linkit liitetiedostoihin (`Liitetiedosto`), jotka avautuvat helposti (esim. upotettu PDF-lukija, linkki uuteen välilehteen).
        *   Mahdollinen strukturoitu sisältö (`sisältö_data`).
    *   **Oikea/Alaosa:** Arviointilomake.
        *   Näyttää haasteen `Arviointikriteeri`-hierarkian selkeästi (esim. sisennetyllä listalla tai laajennettavilla osioilla). **Arvioija näkee vain ne kriteerit, jotka eivät ole `admin_vain=True`, ellei hänelle ole erikseen määritelty tiettyjä kriteereitä `KriteeriArvioija`-mallin kautta (nice-to-have), jolloin hän näkee vain määritellyt kriteerit.**
        *   Kullekin näytettävälle `KRITEERI`-tyyppiselle kriteerille:
            *   Kriteerin nimi (`nimi`), koodi (`koodi`), kuvaus (`kuvaus`).
            *   Ilmoitus maksimipisteistä (`maksimipisteet`) ja mahdollisesta kynnysarvosta (`kynnysarvo`).
            *   Syöttökenttä pisteille (`Arviointi.pisteet`) - esim. numerokenttä, liukusäädin, tai valintanapit (riippuen `maksimipisteet`-arvosta). Validointi suhteessa maksimipisteisiin.
            *   Tekstikenttä kommenteille (`Arviointi.kommentti`).
        *   Mahdollisuus lisätä kommentteja myös `RYHMÄ`-tason kriteereille (jos tämä toiminnallisuus päätetään toteuttaa).
        *   **Tallennus:** Automaattinen tallennus (autosave) tai selkeä "Tallenna luonnos" / "Merkitse valmiiksi" -painike. Jos `Arviointi`-malliin lisätään tila, tämä painike päivittäisi sen.
*   **Muut Arvioijat (Valinnainen Näkyvyys):**
    *   Jos `Haaste.nayta_pisteet_arvioinnin_aikana` on `True`, näytetään (mahdollisesti anonyymisti) muiden arvioijien antamat pisteet *sen jälkeen kun* oma arvio on tallennettu tai vaihtoehtoisesti kun Haasteen tai Hakemuksen arvioinnin tila muuttuu 'Valmis'.
    *   Jos `Haaste.nayta_kommentit_arvioinnin_aikana` on `True`, näytetään muiden kommentit vastaavasti. Tämä voi olla erillinen välilehti tai osio.
*   **Navigointi:** Helppo siirtyminen edelliseen/seuraavaan hakemukseen haasteen sisällä.
*   **Keskustelu:** Jos sallittu, linkki tai upotettu näkymä hakemuksen keskusteluun (`HakemusViesti`).

**4. Hakemuksen keskustelunäkymä (Application Discussion View):**
Nice to have.

*   **Tarkoitus:** Käydä keskustelua tietystä hakemuksesta (jos sallittu).
*   **Sisältö:**
    *   Näyttää viestiketjun (`HakemusViesti`).
    *   Mahdollisuus uusien viestien kirjoittamisen ja vastaamisen olemassaoleviin (`parent`-linkki).
    *   Näkyvyys riippuu rooleista ja pääsyoikeuksista hakemukseen. Arvioijat näkevät yleensä toistensa ja adminien viestit.

**Yleiset UX-periaatteet arvioijalle:**

*   **Selkeys:** Näkymien tulee olla selkeitä ja johdonmukaisia. Arvioijan tulee aina tietää, missä kohtaa prosessia hän on.
*   **Tehokkuus:** Minimoidaan klikkausten määrä. Automaattinen tallennus ja sujuva navigointi hakemusten välillä ovat tärkeitä.
*   **Konteksti:** Hakemuksen tiedot ja arviointilomake näkyvät samanaikaisesti, jotta tietoihin ei tarvitse jatkuvasti hyppiä edestakaisin.
*   **Visuaalinen palaute:** Selkeä indikaatio arviointien tilasta (aloittamatta, kesken, valmis). Värimerkkejä tai ikoneita voidaan hyödyntää.
*   **Ohjeistus:** Kriteerien kuvaukset ja mahdolliset lisäohjeet tulee olla helposti saatavilla arviointinäkymässä.

### 6.3 Ylläpitäjän seurantanäkymä (Admin monitoring dashboard)

**Tarkoitus:** Tarjota ylläpitäjille (admin-tasoiset käyttäjät) reaaliaikainen yleiskuva arviointien etenemisestä kaikissa kampanjoissa ja haasteissa, joihin heillä on pääsy. Auttaa tunnistamaan pullonkauloja ja seuraamaan prosessin aikataulua.

**Sijainti:** Voi olla oma pääsivunsa ylläpitäjän käyttöliittymässä tai osio yleisessä kojelaudassa.

**Sisältö ja toiminnallisuudet:**

1.  **Kampanja-tason yleiskatsaus:**
    *   Lista aktiivisista kampanjoista (`Kampanja.tila` esim. 'Arvioinnissa', 'Avoinna hakemuksille').
    *   Kullekin kampanjalle näytetään:
        *   Nimi (`Kampanja.nimi`).
        *   Tila (`Kampanja.tila`).
        *   Haasteiden lukumäärä kampanjassa.
        *   Yleinen arvioinnin eteneminen kampanjassa (esim. prosenttiosuus haasteista, joissa arviointi on valmis, tai keskimääräinen eteneminen haasteissa).
        *   Linkki kampanjan tarkempiin tietoihin (ylläpitonäkymä tai alla kuvattu haastetason näkymä).

2.  **Haaste-tason yleiskatsaus (voidaan näyttää kampanjakohtaisesti tai kaikki yhdessä listassa):**
    *   Lista haasteista, joissa arviointi on käynnissä tai päättynyt (`Haaste.tila` esim. 'Hakemukset arvioitavana', 'Arviointi päättynyt').
    *   Kullekin haasteelle näytetään:
        *   Haasteen nimi (`Haaste.nimi`) ja linkki kampanjaan.
        *   Haasteen tila (`Haaste.tila`).
        *   Hakemusten kokonaismäärä (`Haaste.hakemukset.count()`).
        *   **Arvioinnin eteneminen:**
            *   Kuinka moni hakemus on arvioitu kaikkien siihen määriteltyjen arvioijien toimesta (esim. "15 / 50 hakemusta valmiina").
            *   Prosentuaalinen eteneminen (esim. perustuen siihen, kuinka monta `Arviointi`-objektia on luotu suhteessa odotettuun maksimimäärään = hakemukset \* kriteerit \* arvioijat).
            *   Visuaalinen etenemispalkki.
        *   Määriteltyjen arvioijien lukumäärä.
        *   Arvioinnin määräaika (`Haaste.arvioinnin_paattymisaika`).
        *   Linkki haasteen tarkempiin tietoihin (ylläpitonäkymä tai alla kuvattu arvioijakohtainen näkymä).

3.  **Haasteen arvioijakohtainen eteneminen:**
    *   Haastekohtaisesti tarjotaan näkymä, joka listaa haasteeseen liitetyt arvioijat (`HaasteKayttaja`, rooli='arvioija').
    *   Kullekin arvioijalle näytetään:
        *   Arvioijan nimi.
        *   Kuinka monta hakemusta kyseinen arvioija on arvioinut valmiiksi / aloittanut tässä haasteessa.
        *   Mahdollisesti viimeisimmän arvioinnin ajankohta.

4.  **Suodatus ja järjestely:**
    *   Mahdollisuus suodattaa näkymää kampanjan tai haasteen tilan, määräaikojen tai nimen perusteella.
    *   Mahdollisuus järjestää listoja eri sarakkeiden mukaan (esim. eteneminen, määräaika).

5.  **Huomiota vaativat kohteet:**
    *   Näkymä voisi korostaa haasteita, joiden määräaika lähestyy tai joissa eteneminen on hidasta verrattuna muihin.

## 7. Avoimet kysymykset

*Listaa asiat, jotka vaativat vielä keskustelua tai selvennystä.*

**Kampanja (Campaign):**
*   Tarvitaanko `jarjestaja_taho`-kentän sijaan/lisäksi erillinen `Organisaatio`-objekti? (Todennäköisesti kyllä).
*   Miten ulkoasun kustomointi tarkalleen toteutetaan ja periytyy/vaikuttaa haasteisiin?

**Haaste (Challenge):**
*   Miten arviointikriteerien rakenne (yksi taso, monta tasoa, ryhmät) tarkalleen mallinnetaan ja liitetään haasteeseen? (Ks. suunnittelumuistion pohdinta eri projektien tarpeista).
*   Tarvitaanko tarkempaa tilanhallintaa (esim. erilliset tilat hakemusten vastaanotolle ja arvioinnille)? (Lisätty ehdotukseen).
*   Miten haastekohtaiset admin-roolit ja kampanja-admin-roolit eroavat oikeuksiltaan?

**Arviointikriteeri (EvaluationCriterion):**
*   Miten painokertoimet lasketaan ja vaikuttavat hierarkian eri tasoilla? Periikö aliryhmä/kriteeri yläryhmän painokertoimen vai lasketaanko painotus suhteessa sisaruksiin? (Tärkeä määrittely laskentalogiikkaa varten‼️)
*   Miten kommentointi tarkalleen toimii? Voiko kommentteja liittää myös 'RYHMÄ'-tyyppisille objekteihin, kuten vanhassa mallissa mainittiin? (Todennäköisesti kyllä, `Arviointi`-objektin kautta).
*   Tarvitaanko lisäkenttiä ohjeistamaan arvioijaa kriteerin osalta?
*   Miten varmistetaan, että vain `KRITEERI`-tyyppisillä objekteilla on `maksimipisteet` ja `kynnysarvo`? (Voidaan validoida mallin tasolla). Vai voivatko ne olla myös `RYHMÄ`-tyyppisille kriteereille?

**Arviointi (Evaluation/Score):**
*   Miten käsitellään tilanne, jos arviointikriteeriä muokataan (esim. `maksimipisteet` muuttuu) sen jälkeen, kun arviointeja on jo annettu? (Vaatii validointia/logiikkaa).
*   Haaste pitää voidan lukita Haaste-adminin toimesta, jotta sen arviointikriteerejä ei voi enää muuttaa.
*   Tarvitaanko erillinen tila arvioinnille (esim. 'Luonnos', 'Valmis')? (Mahdollisesti hyödyllinen).
*   Miten mahdolliset kynnysarvon (`kriteeri.kynnysarvo`) alitukset merkitään tai raportoidaan?
*   Pitäisikö kommentointi olla mahdollista myös 'RYHMÄ'-tyyppisille kriteereille, kuten vanhassa mallissa mainittiin? Jos kyllä, pitäisikö `kriteeri`-kentän viitata myös ryhmiin, ja miten `pisteet` tällöin käsitellään? (Tämä lisäisi kompleksisuutta, harkitaan tarkkaan tarvetta).

**Hakemus (Application/Tender/Proposal/Offer):**
*   Miten liitetiedostot tarkalleen mallinnetaan ja tallennetaan (`Liitetiedosto`-objekti)? Tarvitaanko metatietoja (tiedostonimi, tyyppi, koko)?
*   Miten hallitaan tilannetta, jossa hakemuksen voi jättää sekä rekisteröitynyt käyttäjä että ulkopuolinen taho? Onko `jättäjä_käyttäjä` ja `hakija_*`-kentät riittävä yhdistelmä?
*   Tarvitaanko tarkempia kenttiä hakemuksen sisältöön liittyen (esim. budjetti, avainsanat) vai riittääkö `sisältö_data` ja liitteet?
*   Miten hakemuspohjia tai -lomakkeita hallitaan ja linkitetään haasteeseen? (Tämä voi olla osa Haasteen määrittelyä).
*   **Hakemuksen siirtyminen haasteiden välillä:** Miten mallinnetaan ja hallitaan tilanne, jossa hakemus voi siirtyä haasteesta toiseen (esim. esikarsinnasta jatkoarviointiin)?
    *   Vaikka arvioinnit säilyvät, tarvitaanko erillinen mekanismi (kuten `HakemusHistoria`-malli) seuraamaan, missä haasteessa hakemus on ollut milloinkin?
    *   Miten varmistetaan, että arvioijalle näytetään oikeat ja relevantit hakemuksen tiedot kussakin arviointivaiheessa (haasteessa)? Esimerkiksi esikarsinnassa voidaan näyttää vain tiivistelmä, kun taas jatkoarvioinnissa kaikki tiedot ja liitteet. Pitääkö `Hakemus`-mallia laajentaa vai riittääkö käyttöliittymälogiikka ohjaamaan näytettävää dataa `Haaste`-kontekstin perusteella? Vai kannattaisiko Hakemuksesta tallentaa uusi versio jokaiseen arviointivaiheeseen? (Tämä vaatii tarkempaa suunnittelua, koska Application ID olisi eri haasteissa sama.)

**Liitetiedosto (Attachment):**
*   Missä ja miten tiedostot fyysisesti tallennetaan (esim. paikallinen tiedostojärjestelmä, pilvitallennus kuten S3)? Tämä vaikuttaa `tiedosto`-kentän toteutukseen.
*   Tarvitaanko tarkempia pääsynhallintasääntöjä liitetiedostoille (esim. kuka voi ladata/poistaa)?
*   Miten käsitellään tiedostojen versiointia, jos hakemusta päivitetään?

**Kampanjan käyttäjä (CampaignUser):**
*   Miten haastekohtaisten ja kampanjatason roolien vuorovaikutus ja oikeuksien periytyminen tarkalleen toteutetaan ja validoidaan? (Peruslogiikka kuvattu toiminnallisuudessa, mutta vaatii tarkempaa suunnittelua).

**Haasteen käyttäjä (ChallengeUser):**
*   Tarvitaanko tarkempia rooleja haastetasolla?
*   Miten haastekohtaisten ja kampanjatason roolien vuorovaikutus ja oikeuksien periytyminen tarkalleen toteutetaan ja validoidaan? (Peruslogiikka kuvattu toiminnallisuudessa, mutta vaatii tarkempaa suunnittelua).

**HakemusViesti (ApplicationMessage):**
*   Ketkä käyttäjät (mitkä roolit) tarkalleen voivat nähdä keskustelun ja lähettää viestejä kuhunkin hakemukseen? (Todennäköisesti ne, joilla on pääsy hakemukseen roolien perusteella).
*   Tarvitaanko viesteille muokkaus- tai poistotoimintoa? Jos kyllä, millä ehdoilla ja kenen toimesta?
*   Miten uusista viesteistä ilmoitetaan käyttäjille (esim. sähköposti-ilmoitukset)?

**Kampanjan käyttäjä (CampaignUser):**
*   Miten haastekohtaisten ja kampanjatason roolien vuorovaikutus ja oikeuksien periytyminen tarkalleen toteutetaan ja validoidaan? (Peruslogiikka kuvattu toiminnallisuudessa, mutta vaatii tarkempaa suunnittelua).

**KriteeriArvioija (CriterionEvaluatorAssignment):**
*   Miten tämän ominaisuuden hallinta integroidaan ylläpitäjän käyttöliittymään (esim. `Haaste`- tai `HaasteKayttaja`-näkymään)?
*   Onko tämä ominaisuus todella tarpeellinen ensimmäisessä vaiheessa, vai voidaanko se jättää myöhempään kehitykseen?
