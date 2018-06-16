Anleitung zur Kometen-Fotometrie mit AIRTOOLS (v2.2)
====================================================

-   [Einführung](#einführung)
-   [Kometen-Aufnahmen](#kometen-aufnahmen)
-   [Installation](#installation)
    -   [Vorbereitung eines Rechners mit Windows oder MacOS Betriebssystem](#vorbereitung-eines-rechners-mit-windows-oder-macos-betriebssystem)
        -   [VirtualBox](#virtualbox)
        -   [Linux Installations-Medium](#linux-installations-medium)
        -   [Linux Live-System als VirtualBox VM](#linux-live-system-als-virtualbox-vm)
        -   [Austausch von Dateien zwischen Host und virtualisiertem Linux PC](#austausch-von-dateien-zwischen-host-und-virtualisiertem-linux-pc)
    -   [Installation der AIRTOOLS Software](#installation-der-airtools-software)
-   [Der Airtools - Launcher](#der-airtools---launcher)
    -   [Formular “Project”](#formular-project)
    -   [Formular “New Site”](#formular-new-site)
    -   [Formular “Image Set”](#formular-image-set)
    -   [Formular “New Instrument”](#formular-new-instrument)
    -   [Formular “Launch”](#formular-launch)
-   [AIRTOOLS Tasks](#airtools-tasks)
    -   [SAOImage als grafische Oberfläche](#saoimage-als-grafische-oberfläche)
    -   [AIRTOOLS Tasks im Überblick](#airtools-tasks-im-überblick)
    -   [Astrometrie](#astrometrie)
    -   [Bild-Hintergrund](#bild-hintergrund)
    -   [Ermittlung der PSF](#ermittlung-der-psf)
    -   [Kometen-Extraktion](#kometen-extraktion)
    -   [Manuelle Messungen](#manuelle-messungen)
    -   [Fotometrie](#fotometrie)
-   [Projektsicherung](#projektsicherung)
-   [Anhang](#anhang)
    -   [Dateien im Projektordner](#dateien-im-projektordner)
    -   [Xubuntu Linux - Erste Schritte](#xubuntu-linux---erste-schritte)
    -   [Installation von Xubuntu Linux in VirtualBox VM](#installation-von-xubuntu-linux-in-virtualbox-vm)

Einführung
==========

AIRTOOLS ist ein Akronym für **A**stronomical **I**mage **R**eduction **TOOLS**et und steht für eine Sammlung von Programmen zur Verarbeitung von astronomischen Bilddaten, die mit CCD oder Digitalkamera aufgenommen wurden. Die Software bietet Funktionen zur grundlegenden Bildbearbeitung (z.B. RAW-Entwicklung, Bias-, Dark-, Flat-Korrektion), zur automatischen Objekterkennung und zum Registrieren und Stacken von Bildserien sowie zur Astrometrie und Fotometrie unter Verwendung verschiedener Referenzkataloge.

Darüber hinaus existieren spezialisierte Tools zur Auswertung von Kometen-Aufnahmen. Diese haben das Ziel, eine zur visuellen Gesamthelligkeitsbestimmung adäquate Fotometrie zu ermöglichen. Neben der höheren Reichweite der Aufnahmen wird vor allem eine Reproduzierbarkeit der Helligkeitsmessung erreicht. Außerdem werden subjektive Einflüsse und methodologische Differenzen zwischen den Beobachtern weitestgehend ausgeschlossen.

Die AIRTOOLS Software benötigt ein Linux-Betriebssystem. Dies muß aber nicht zwingend auf dem Rechner des Anwenders installiert sein, sondern kann entweder in einer virtuellen Umgebung laufen oder von einem Linux Live-System (d.h. von einem bootbaren DVD- bzw. USB-Medium oder einer ISO-Imagedatei) gestartet werden.

Die einzelnen Programme sind vollständig als Kommandozeilen-Programme einsetzbar und somit in Skripten gut kombinierbar. Die wesentlichen Werkzeuge zur Kometen-Fotometrie sind zur leichteren Handhabung über ein grafisches Nutzerinterface bedienbar. Die Erläuterung ausschließlich jener Werkzeuge ist Gegenstand dieser Anleitung.

Die AIRTOOLS Programmsammlung verwendet eine ganze Reihe von Programmen die Bestandteil der meisten Linux Distributionen sind, wie z.B. ImageMagick, GraphicsMagick, Netpbm und Gnuplot. Außerdem werden frei verfügbare, leistungsfähige Programme aus dem Umfeld der professionellen Astro-Bildverarbeitung benutzt. Das sind insbesondere

-   [SAOImage DS9](http://ds9.si.edu/site/Home.html): Image Viewer mit Katalog- und Analyse-Werkzeugen
-   [Astromatic Software](http://www.astromatic.net) von E. Bertin: Automatische Objekterkennung (sextractor), Astrometrie (scamp), Bildtransformation und Stacking (swarp), Objektmodellierung (skymaker) u.a.
-   [Stilts](http://www.starlink.ac.uk/stilts/) von M. Taylor: Analyse, Filterung und Transformation von tabellarischen Daten (u.a. im FITS Format)
-   [WCSTools](http://tdc-www.harvard.edu/software/wcstools/) von J. Mink: Werkzeuge zur Erzeugung und Manipulation von Bild-Koordinatensystemen

Die AIRTOOLS Software ist frei verfügbar. Der Quellcode ist auf der Projektseite <https://github.com/ewelot/airtools> zu finden. Leicht installierbare Programmpakete werden für ausgewählte Linux Distributionen zur Verfügung gestellt.

Für Anregungen, Fragen oder einfach nur Feedback zu Programm oder Anleitung erreichen Sie mich unter: <t_lehmann@freenet.de>

Viel Erfolg!

Thomas Lehmann

Weimar, im September 2017

Kometen-Aufnahmen
=================

Sollen Aufnahmen zur späteren Kometen-Fotometrie gewonnen werden, empfielt es sich, anstatt einer langen Belichtung mehrere kürzere Belichtungen als Serie aufzunehmen. Da die Größe der Koma zumeist weit unterschätzt wird, sollte auf ein ausreichend großes Gesichtsfeld geachtet werden. Es sollten möglichst wenige gesättigte Sterne in den Bereich der Koma fallen.

Zur Trennung von Komet und Hintergrundsternen werden zwei Bilddateien benötigt: zum einen das auf den Kometen gestackte Bild, das die Sterne als Spuren enthält (im folgenden: Kometen-Stack) und zum zweiten das auf die Sterne gestackte Bild, das die Kometenspur zeigt (Sternen-Stack).

Die Bildkalibration unter Verwendung von Bias, Dark, Flat mit den Mitteln der AIRTOOLS wird an dieser Stelle nicht beschrieben, ebensowenig das Stacken der Einzelbilder. Dazu existieren auch unter den zumeist benutzten Betriebssystemen Windows und MacOS ausgereifte Programme, die den meisten Astrofotografen geläufig sind.

Die gestackten Bilder, die mit den AIRTOOLS verarbeitet werden sollen, müssen folgende **Voraussetzungen** erfüllen:

-   Die gestackten Bilder müssen im FITS-Format vorliegen. Die Pixel haben Intensitäten (auch counts oder ADU) im 16bit Dynamikbereich, also Werte zwischen 0 und 65535. Die Bildgröße beider Stacks muß gleich sein.
-   Die Linearität des mit dem Detektor empfangenen Signals muß bei allen bisher erfolgten Arbeitssschritten (z.B. RAW-Entwicklung, Bias-, Dark-, Flatkalibration, Stacken) erhalten geblieben sein.
-   Es sollte kein Abzug des Hintergrundsignals erfolgen, auch keine Ebnung, d.h. ein natürlicher Helligkeitsgradient des Himmels soll in der Aufnahme erhalten bleiben.
-   Der Intensitäts-Nullpunkt (“Schwarzpunkt”, d.h. die counts ohne Lichteinfall) muß bekannt sein (idealerweise bei 0).
-   Die Stacks sind aus Mittelwert-Bildung entstanden. Die Anwendung eines Median-Filters beim Stacken ist nicht erlaubt.
-   Die Beobachtungszeit (idealerweise Mitte der Belichtungen) muß im FITS-Header enthalten sein, entweder als JD oder als DATE-OBS (Datum und Zeit in UT).
-   Genäherte Koordinaten der Bildmitte werden aus den Feldern RA (bzw. OBJCTRA) und DEC (bzw. OBJCTDEC) im FITS-Header übernommen. Sind diese nicht vorhanden, werden die Koordinaten des Kometen zur Beobachtungszeit laut Ephemeriden verwendet und es wird angenommen, daß sich der Komet nahe der Bildmitte befindet (maximal erlaubte Distanz: ca. 10% der Bildgröße).

Installation
============

Im Folgenden wird die Installation der AIRTOOLS für Nutzer beschrieben, die einen PC mit Windows oder MacOS Betriebssystem besitzen. Im ersten Teil wird dabei ein virtualisiertes Linux-System gestartet. Nutzer, die bereits einen Linux-Rechner betreiben, können dieses Unterkapitel 3.1 überspringen. Im zweiten Teil wird die eigentliche AIRTOOLS-Installation im (eventuell virtualisierten) Linux-System beschrieben.

Die Hardware-Voraussetzungen zum Arbeiten mit den AIRTOOLS sind nicht hoch. Jeder PC oder Laptop, der in den letzten ca. 7 Jahren angeschafft wurde, ist dazu geeignet. Allerdings ist ein großer Bildschirm, wie bei allen Programmen der Bildbearbeitung, von Vorteil.

Ein Internet-Anschluß ist zwingend erforderlich, da diverse Daten wie Ephemeriden und astrometrische und fotometrische Referenzkataloge online abgefragt werden.

Vorbereitung eines Rechners mit Windows oder MacOS Betriebssystem
-----------------------------------------------------------------

Ein virtualisierter PC - auch virtuelle Machine oder kurz VM genannt - ist eine ideale Lösung, um eine von den Daten und Programmen des eigentlichen Rechners (Host) abgesetzte, isolierte Umgebung zu schaffen in der beliebige Betriebssysteme und Anwendungen laufen. Es ist auch möglich, mehrere VMs gemeinsam produktiv parallel zum Host zu benutzen - gerade so, als ob man mehrere Rechner in einem Netzwerk betreiben würde.

Um die AIRTOOLS auf einem virtualisierten Linux-PC installieren zu können benötigt man eine Virtualisierungs-Software, die auf dem Host-PC installiert wird und ein Linux Installations-Medium (z.B. als DVD oder ISO-Datei).

### VirtualBox

VirtualBox (<http://www.virtualbox.org>) ist eine ausgereifte, frei erhältliche Virtualisierungs-Software. Es muß die zum (Host-) Betriebssystem passende Version von der Download-Seite heruntergeladen und installiert werden. Anschließend erfolgt die Installation des sogenannten *VirtualBox Extension Pack*:

-   Herunterladen des *VirtualBox Extension Pack* von der gleichen Download-Seite
-   Starten des Oracle VM VirtualBox Managers (VirtualBox Desktop Icon)
-   Im Manager unter dem Menüpunkt Datei/Einstellungen zum Reiter Zusatzpakete wechseln
-   Über das blaue Symbol am rechten Fensterrand kann das Paket hinzugefügt werden: Extension Pack Datei auswählen, öffnen und installieren.

### Linux Installations-Medium

Linux gibt es in sehr unterschiedlichen Ausprägungen, wobei das Betriebssystem und ein großer Teil von Anwendungssoftware gebündelt als sogenannte Distribution angeboten wird. Prinzipiell lässt sich die AIRTOOLS-Software auf einer beliebigen Linux-Distribution installieren, da alle benötigten Komponenten auch im Quellcode verfügbar sind. Um jedoch den Installationsaufwand zu minimieren, wird die Verwendung einer Linux-Version empfohlen, für die alle Programme als Binärpakete verfügbar sind (sie sind somit kompiliert und leicht installierbar bzw. deinstallierbar). Dies sind zur Zeit die 64bit Versionen von

-   Ubuntu 18.04 “Bionic” (und Varianten wie Xubuntu)
-   Ubuntu 16.04 “Xenial” (und Varianten wie Xubuntu)
-   Debian 9 “Stretch”

In der weiteren Anleitung wird Xubuntu Linux (<https://xubuntu.org/>) in der Version 16.04 LTS (64bit) verwendet. Sie müssen die entsprechende ISO-Image Datei aus dem Download-Bereich herunterladen (aktuell z.B. [xubuntu-16.04.4-desktop-amd64.iso](http://ftp.uni-kl.de/pub/linux/ubuntu-dvd/xubuntu/releases/16.04/release/xubuntu-16.04.4-desktop-amd64.iso)).

### Linux Live-System als VirtualBox VM

Die meisten (großen) Linux-Distributionen bieten ihre Software mittlerweise als Live-System an, d.h. das Betriebssystem und die Anwendungen befinden sich auf einem bootbaren Medium (CD, DVD, ISO-Datei). Nach dem Booten dieses Mediums ist das Linux Live-System voll funktionsfähig und kann beliebig getestet werden. Bei Bedarf kann das laufende System auf eine Festplatte installiert werden.

So funktioniert das auch mit der Xubuntu ISO-Datei, die in einer VirtualBox VM direkt als Bootmedium verwendet werden kann. Dazu sind folgende Schritte notwendig:

-   Oracle VM VirtualBox Manager starten
-   Erzeugung einer neuen VM:
    -   Werkzeugleiste *Neu*
    -   Name: Xubuntu-16.04, Typ: Linux, Version: Ubuntu (64bit)
    -   Speicher: ca. Hälfte des RAM vom Hostsystem, mind. 2000 MB
    -   Platte: keine Festplatte
-   Einstellungen der VM vornehmen:
    -   Werkzeugleiste *Ändern*
    -   unter *System* Reiter Hauptplatine: Box “Hardware-Uhr in UTC” deaktivieren
    -   unter *System* zu Reiter Prozessor: Anzahl auf Hälfte der CPUs des Hostsystems erhöhen
    -   unter *Anzeige* zu Tab Bildschirm: Grafikspeicher auf 32 MB erhöhen
    -   unter *USB*: USB-3.0-Controller aktivieren
-   ISO-Datei als Bootmedium einlegen:
    -   unter *Massenspeicher*, Controller IDE auf CD “leer” klicken
    -   über das CD-Symbol ganz rechts am Fensterrand die Auswahlliste für das optische Laufwerk öffnen und darin den ersten Eintrag “Datei für optisches Medium auswählen …” wählen
    -   im Dateimanager die Xubuntu ISO-Datei auswählen, es erscheint schließlich der ISO-Dateiname unter Controller IDE neben dem CD Symbol
    -   Box “Live-CD/DVD” am rechten Fensterrand aktivieren
    -   das Einstellungen-Fenster mit “OK” schließen
-   Virtuelles Linux System booten:
    -   Über den Knopf *Starten* in der Werkzeugleiste des Managers wird der Bootvorgang von Xubuntu Linux in der virtuellen Maschine gestartet. Diese erscheint als neues Fenter mit einer Menüleiste (oben) zum Zugriff auf Einstellungen der VM und dem darunter befindlichen “Bildschirm” des virtuellen Rechners.
    -   Eventuell erscheinende Meldungen von VirtualBox am oberen Fensterrand der VM können (nach dem Lesen) geschlossen werden.
    -   Nach einiger Zeit (ca 30-60 s) erscheint auf dem Bildschirm der VM das Fenster *Install* in dem links als Sprache “Deutsch” gewählt werden kann (2 Einträge über English).
    -   Danach “Xubuntu ausprobieren” wählen und warten bis der Bootvorgang abgeschlossen wird. Im Live-System wird dabei der Nutzer “xubuntu” automatisch angemeldet.

Auf dem gestarteten Xubuntu Desktop befindet sich das Programm-Menü unter dem kleine blau-weißen Icon in der linken oberen Ecke. Im geöffneten Programm-Menu befindet sich rechts unten ein Symbol für den Ausschaltknopf, über den das virtuelle Linux-System heruntergefahren werden kann. Die dabei erscheinende Meldung zur Entfernung des Installationsmediums kann ignoriert werden. Nach Betätigen der Enter-Taste wird die VM geschlossen. Weitere Informationen zur Orientierung auf dem Xubuntu Desktop befinden sich im [Anhang](#xubuntu-linux---erste-schritte).

Beim ersten Start erscheint der Xubuntu Desktop in einer geringen Größe, die zum Arbeiten mit den AIRTOOLS nicht ausreichend wäre. Eine Möglichkeit der Vergrößerung des virtuellen Bildschirms ist folgende:

-   Fenster der VM durch Ziehen der Ränder auf gewünschte Größe bringen
-   Nutzer im Xubuntu Linux abmelden. Dazu im geöffneten Programm-Menü den Ausschaltknopf betätigen und Abmelden wählen.
-   Der Bildschirm startet in neuer Größe und die Anmeldemaske erscheint.
-   Einloggen als Nutzer “xubuntu” ohne Paßwort.

Das Live Linux-System läuft komplett im RAM des Hosts, wobei die in der VM-Konfiguration angegebene Speichergröße zu gleichen Teilen als RAM für das Betriebssystem und Anwendungen und als “Plattenplatz” zur Verfügung gestellt wird. D.h. bei 2 GB zugewiesenem VM Speicher können maximal 1 GB für neue/geänderte Dateien benutzt werden. Dazu zählen neu installierte Anwendungen und Nutzerdaten in gleicher Weise.

Alle Änderungen, die an diesem Linux-System vorgenommen werden, sind nur solange existent, wie das System läuft. Beim Herunterfahren gehen sie verloren. Das gilt gleichermaßen auch für alle neu erzeugten oder modifizierten Dateien sofern sie nich auf einen externen Datenträger geschrieben werden. Nach dem Booten eines Live-Systems hat man somit stets einen identischen Ausgangszustand. Das hat den Vorteil, daß das Linux Live-System auf keine Weise unbrauchbar gemacht werden kann. Man hat eine ideale Testumgebung für Anwendungen und Spielwiese für eigene Experimente. Nachteile der Nutzung der AIRTOOLS in solch einem Live-System sind:

-   wenig Platz für eigene Dateien
-   alle Ergebnisse müssen auf ein externes Medium (z.B. USB-Platte) gesichert werden, bevor das virtuelle Linux-System heruntergefahren wird
-   nach jedem Bootvorgang ist die AIRTOOLS Installation, die im folgenden Abschnitt beschrieben wird, zu wiederholen

Abhilfe für alle genannten Punkte schafft die permanente Installation des Xubuntu-Linux Systems auf eine virtuelle Festplatte innerhalb der VM (siehe [Anhang](#installation-von-xubuntu-linux-in-virtualbox-vm)). Für erste Schritte und Tests der AIRTOOLS Software ist die Arbeit mit dem Live-System hingegen bestens geeignet.

### Austausch von Dateien zwischen Host und virtualisiertem Linux PC

Es gibt verschiedene Wege, um Dateien zwischen dem Hostrechner (Windows-PC) und einem virtualisierten Rechner (z.B. Linux in VM) auszutauschen. Eine einfache Möglichkeit besteht in der Verwendung eines USB Sticks (bzw. einer USB Festplatte) - genauso, als würde man Dateien zwischen zwei realen Computern transportieren.

Auf dem Hostrechner wird der USB Stick mit Daten beschrieben. Das sind die FITS Bilder von Sternenstack, Kometenstack und im Idealfall auch die kalibrierten Einzelbilder. Es empfiehlt sich, die Daten von verschiedenen Beobachtungsnächten in getrennten Ordnern abzulegen. Wenn der Schreibvorgang auf den USB Stick beendet ist, kann er an die virtuelle Maschine übergeben werden. Dazu im Fenster der laufenden VM über den Menüpunkt *Geräte/USB* den Geräteeintrag zum USB Stick aktivieren.

Der USB Stick wird im laufenden virtualisierten Linux-System erkannt und automatisch eingebunden, genauso als würde man den Stick am USB-Port eines realen Linux-PC einstecken. Es erscheint ein entsprechendes Desktop-Symbol und Dateien können von Stick gelesen oder auf ihn kopiert werden.

Das Entfernen des Sticks vom Linux-System geschieht mittels Klick mit rechter Maustaste auf das USB-Stick-Symbol und *Datenträger auswerfen*. Jetzt kann er vom virtualisierten PC “abgezogen” werden. Dazu wird im Fenster der VM über den Menüpunkt Geräte/USB der Geräteeintrag zum USB Stick deaktiviert.

Installation der AIRTOOLS Software
----------------------------------

Die im Folgenden beschriebene Installation von Binärpaketen erfordert ein laufendes Linux-System. Der gesamte Installationsvorgang dauert bei Vorhandensein einer DSL-Verbindung zum Internet nur wenige Minuten. Unter Xubuntu-Linux sind folgende Arbeitsschritte erforderlich:

-   Das [Installationsprogramms](https://github.com/ewelot/airtools/raw/master/install_deb.sh) aus dem GitHub Repository herunterladen:
    -   Im Programm-Menü den Internetnavigator (Firefox) starten und in der Adressleiste den Link zur Projektseite https://github.com/ewelot/airtools eingeben.
    -   Dem Link zum Installationsprogramm `install_deb.sh` folgen.
    -   Die Quelldatei ist über den Knopf “Raw” am rechten Seitenrand erreichbar. Dort mit Klick der rechten Maustaste *Save Link As …* wählen und die Datei im voreingestellten Ordner Downloads speichern.
    -   Den Webbrowser Firefox schließen.
-   Die Dateiverwaltung (Browser zur Navigation im Datei-System) öffnen durch Doppelklick auf Icon *Persönlicher Ordner* und in den Ordner wechseln, in dem das Installationsprogramm abgelegt wurde (standardmäßig Ordner “Downloads”).
-   In Dateiverwaltung unter Menu *Datei* den Eintrag *Terminal hier öffnen* wählen, wodurch ein Terminal-Fenster erscheint. Das Fenster der Dateiverwaltung kann jetzt geschlossen werden.
-   Installationsvorgang starten durch Eingabe des folgenden Kommandos im Terminal:

    `sudo bash install_deb.sh`
-   Hinweis: Eine während der Vorbereitung des Installationsvorgangs auftretende Fehlermeldung von *appstreamcli* kann ignoriert werden.

Das Live-System, das aus der ISO-Datei gestartet wird, beinhaltet nur eine begrenzte Software-Auswahl. Für das Funktionieren der AIRTOOLS Software müssen daher eine Reihe von Softwarepaketen nachinstalliert werden. Dies geschieht wärend der AIRTOOLS Installation automatisch (Download von insgesamt ca. 90 MB aus dem Internet). Nach der erfolgreichen Installation wird ein neuer Eintrag im Programm-Menü (in der Kategorie Bildung) und ein neues Desktop-Icon mit dem Namen “Airtools” erzeugt. Das Terminal-Fenster mit den Ausgaben des Installationsvorgangs wird nicht mehr benötigt und kann geschlossen werden.

Der Airtools - Launcher
=======================

Zu den für die Auswertung benötigten Daten gehören neben den FITS Bildern der Stacks diverse Zusatzangaben zu den Aufnahmen, zum Beobachtungsinstrument und Aufnahmeort. Zur Einrichtung eines neuen AIRTOOLS-Projektes und zur Abfrage der genannten Metadaten wird ein Hilfsprogramm, der Airtools-Launcher verwendet. Er wird durch Doppelklick auf das Airtools-Icon gestartet.

Formular “Project”
------------------

Der obere Teil des Formulars dient zum Öffnen eines schon vorhandenen Projektes. Soll ein neues Projekt angelegt werden, so sind die unteren Formularfelder auszufüllen.

Base Directory:  
Alle AIRTOOLS-Projekte werden unterhalb eines Basis-Ordners angelegt. Dieses Verzeichnis sollte sich daher auf einer Festplatte (bzw. Partition) mit ausreichend freiem Speicherplatz befinden.

Date of observation:  
Ein Projekt kann mehrere Kometen-Beobachtungen einer Nacht enthalten, auch wenn diese mit unterschiedlichen Teleskopen aufgenommen wurden. Der Name des Projektverzeichnisses wird standardmäßig aus dem Beobachtungsdatum gebildet. Dabei wird das Datum zu Beginn der Nacht im Format “yymmdd” benutzt.

Temporary Directory:  
Ordner für temporäre Dateien. Dies ist unter Linux üblicherweise /tmp.

Observatory Site:  
Hier wird der Beobachtungsort aus einer Liste bekannter Orte ausgewählt. Durch Wahl von “new site” kann in einem gesonderten Formular der Eintrag für einen neuen Beobachtungsort angelegt werden.

<img src="images/launcher_project.png" alt="Airtools-Launcher Formular Project" width="302" />

Formular “New Site”
-------------------

Folgende Angaben eines Beobachtungsortes werden benötigt:

Site ID:  
Die ID muß ein eindeutiges Kürzel aus drei Buchstaben sein.

Location:  
Name des Beobachtungsortes, bestehend aus einem Wort.

TZ-UT:  
Zeitzonendifferenz zu Greenwich (ohne Sommerzeit) in Stunden.

Longitude:  
Geografische Länge in Grad, negativ für Orte östlich von Greenwich.

Latitude:  
Geografische Breite in Grad, positiv für Orte nördlich des Äquators.

Altitude:  
Höhe des Beobachtungsortes über dem Meeresspiegel in Metern.

Jeder Beobachtungsort muß nur einmal erfaßt werden. Danach steht er für alle zukünftigen Projekte zur Verfügung (siehe [oben](#formular-project)).

<img src="images/launcher_site.png" alt="Airtools-Launcher Formular New Site" width="302" />

Formular “Image Set”
--------------------

Eine Kometenbeobachtung (bestehend aus Kometenstack und Sternenstack) basiert auf einer Serie von Einzelbelichtungen - einem *Image Set*. Das vorliegende Formular wird benutzt, um entweder ein bereits vorher definiertes Set auszuwählen oder die Angaben zu einem neuen Set zu erfassen:

Set name:  
Ein in diesem Projekt eindeutiger Kurzname für das *Image Set*, bestehend aus zwei Buchstaben (z.B. co für Komet) und zwei Ziffern (z.B. laufende Nummer der Beobachtung in dieser Nacht). Dieser Setname wird als Basis des Namens von diversen Ergebnisdateien verwendet.

Target comet:  
Bezeichnung des Kometen. Diese wird u.a. verwendet, um Ephemeriden aus der MPC-Datenbank per Webzugriff abzufragen. Die Schreibweise für periodische Kometen ist Nummer mit angehängtem “P” (z.B. 41P), sonst Jahr und Bezeichnung ohne Leerzeichen (z.B. 2015ER61).

Local start time:  
Startzeit der Belichtungsreihe. Diese hat lediglich informativen Charakter im Sinne von Logbuch-Einträgen der Kometenbeobachtungen der Nacht.

Average exposure time:  
Mittlere Belichtungszeit eines Einzelbildes in Sekunden.

Number of exposures:  
Anzahl der Belichtungen die gestackt wurden.

Reference image number for stacking:  
Nummer des Bildes in der Serie, das als Referenzbild beim Stacken benutzt wurde. Wenn nicht angegeben, wird angenommen, daß auf das erste Bild gestackt wurde.

Pixel binning:  
Anzahl der Pixel, die beim Auslesevorgang zusammengefaßt wurden.

Instrument (telescope/camera):  
An dieser Stelle kann aus einer Liste von bereits definierten Beobachtungsinstrumenten selektiert werden. Wurde ein neues Instrument (Teleskop und/oder Kamera) benutzt, muß der Eintrag “add new instrument” gewählt werden.

Comments:  
Feld für die Filterbezeichnung oder andere Angaben.

Image files of individual exposures:  
Liste der beim Stacken verwendeten Einzelbilder (FITS-Dateien), die über den Datei-Browser (rechtes Ordner-Symbol) selektiert werden können. Wenn diese bekannt sind, dann wird die Aufnahmezeit aller Bilder extrahiert und später in den AIRTOOLS-Programmen mit verwendet.

<img src="images/launcher_set.png" alt="Airtools-Launcher Formular Image Set" width="302" />

Formular “New Instrument”
-------------------------

Das Formular dient der Definition eines neuen Aufnahmeinstruments mit den zugehörigen Angaben von Teleskop und verwendeter Kamera. Die Felder sind wie folgt auszufüllen:

Instrument ID:  
Kurzbezeichnung für das benutzte Instrument, bestehend aus 3-6 Buchstaben oder Ziffern. Diese dient der eindeutigen Identifizierung unter allen definierten Beobachtungsinstrumenten, d.h. allen Teleskop-Kamera-Kombinationen.

Focal length:  
Aufnahmebrennweite in mm. Hinweis: Es ist ausreichend, wenn zwei der drei Felder: Focal length, Aperture, F-Ratio ausgefüllt werden.

Aperture:  
Durchmesser der Teleskop- bzw. Objektiv-Öffnung in mm.

F-ratio:  
Öffnungsverhältnis f/D bzw. Blende.

Camera model:  
Modellbezeichnung der Kamera.

Camera and Sensor keys:  
ICQ Schlüssel für [Kamera](https://cobs.si/help?page=ccd_type) und [Sensor](https://cobs.si/help?page=ccd_chip), getrennt durch das Zeichen /, z.B. für Canon 6D: CDS/CFC.

Camera rotation:  
Rotationswinkel der Kamera in Grad (Norden oben = 0°, Norden links = 90°)

Rawbits:  
Anzahl der Bits pro Pixel in einem Farbkanal.

Saturation:  
Grenzwert der Counts (ADU) bis zu dem die Signalwiedergabe linear ist.

Gain:  
Anzahl der Elektronen je ADU. Wenn nicht bekannt, dann kann als Schätzwert 1 eingesetzt werden.

Pixel scale:  
Größe des Bildpunktes am Himmel in Bogensekunden.

Mag zero point:  
Schätzwert für Helligkeitsnullpunkt, d.h. die Sternhelligkeit, die bei 1 Sekunde Belichtungszeit eine Intensität von 1 Count (ADU) erzeugen würde.

Telescope type:  
Auswahl des Teleskop-Typs: Reflector, Refractor, Photo Lens

Camera type:  
Auswahl des Kameratyps: CCD, DSLR

<img src="images/launcher_instrument.png" alt="Airtools-Launcher Formular New Instrument" width="302" />

Zu beachten ist, daß sich die Werte für *Saturation*, *Gain* und *Mag zero point* auf das gestackte Bild geziehen, das möglicherweise in der Intensität gegenüber den ausgelesenen Rohbildern gestreckt ist. Es ist z.B. nicht unüblich, daß DSLR-Aufnahmen mit 14bit je Pixel auf einen 16bit Dynamikbereich gestreckt werden, wonach die Sättigungsgrenze im gestackten Bild bei ca. 60000 ADU liegen kann.

Formular “Launch”
-----------------

Abschließend erfolgt nun die Auswahl der Bilddateien, die mit den AIRTOOLS analysiert werden sollen:

Stack centered on stars:  
Wenn das Feld noch leer ist, dann ist hier die FITS-Datei auszuwählen, die den Sternenstack enthält.

Stack centered on comet:  
Wenn das Feld noch leer ist, dann ist hier die FITS-Datei auszuwählen, die den Kometenstack enthält.

Choose an action:  
Auswahl der Aktion, die nach Klicken des Knopfes *OK* erfolgt. Normalerweise wird dies der Start der grafischen Oberfläche zum Aufruf der AIRTOOLS-Tasks sein. Es besteht aber auch die Möglichkeit, die Dateiverwaltung im Projekt-Ordner zu starten oder für spezielle Experten-Aktionen ein Terminal-Fenster im Projekt-Ordner zu öffnen.

Nach Wahl der Aktion “Launch AIRTOOLS” werden die FITS Bilder konvertiert in 16bit PGM Bilddateien (bzw. PPM bei RGB-FITS Bildern). Die Namen dieser Dateien beginnen mit dem Namen des *Image Sets*. Wurde beispielsweise das Set mit `co01` bezeichnet und handelt es sich um monochrome CCD Aufnahmen, so heißt der umgewandelte Sternenstack `co01.pgm` und der Kometenstack `co01_m.pgm`.

Funktionieren Bildkonvertierung und die Validierung der Header-Informationen, dann wird die Arbeit des Launchers beendet und nach einigen Sekunden das Programm *SAOImage* gestartet, das als grafische Oberfläche für die AIRTOOLS Tasks dient.

<img src="images/launcher_launch.png" alt="Airtools-Launcher Formular Launch" width="302" />

AIRTOOLS Tasks
==============

SAOImage als grafische Oberfläche
---------------------------------

Das Programm *SAOImage* wird als grafisches Frontend zur Interaktion mit FITS Bildern auch an professionellen Sternwarten eingesetzt. Es bietet viele nützliche Funktionen und umfangreiche Hilfe-Informationen. Im Rahmen der AIRTOOLS wird nur ein kleiner Funktionsumfang gebraucht.

Nach Beendigung des Launchers erscheint das Fenster *SAOImage AIRTOOLS*. Es besitzt eine Menüzeile, diverse Informationsfelder, ein kleines Übersichtsbild (mit x-y-Achsen) und ein Lupenfeld (Vergrößerung der Region um den Mauszeiger), darunter zwei Knopfleisten und den großen Bildrahmen und ganz unten einen Intensitätsbalken mit Skale. Sichtbar ist das Bild des Sternenstacks. In einer zweiten Ebene - Rahmen 2, durch Tab erreichbar - befindet sich das Bild des Kometenstacks.

Bei Verwendung kleiner Bildschirme ist es zweckmäßig, die Fontgröße zu verringern, um Platz für ein größeres Bildfeld zu schaffen. Dazu unter Menu *Bearbeiten/Einstellungen* die Einstellungen von

-   GUI Font: helvetica anklicken und Größe z.B. 10 wählen
-   Text Font: courier anklicken und Größe z.B. 10 wählen

und abschließend die Einstellungen speichern. Außerdem kann es hilfreich sein, unter Menü *Ansicht* auf vertikales Layout umzustellen.

Durch folgende Aktionen läßt sich das Aussehen des FITS-Bildes manipulieren:

-   Änderung von Bildhelligkeit und Kontrast durch Klicken und Ziehen der rechten Maustaste. Bei horizontaler Bewegung ändert sich die Helligkeit, bei vertikaler Bewegung der Kontrast.
-   Verkleinern und Vergrößern des Bildausschnitts durch Rollen des Mausrades.
-   Bewegen des Bildausschnitts durch Klicken mit der mittleren Maustaste im Bild oder im kleinen Übersichtsbild (Panner, mit x-y-Achsen). Damit wird ein neues Bildzentrum gewählt.
-   Bildwechsel bei mehreren geladenen Bildern durch Verwendung der Tab-Taste (vorwärts) beziehungsweise Shift-Tab (rückwärts). Wenn mehrere Bilder geladen sind, werden sie standardmäßig einzeln dargestellt. Über den Menüpunkt *Rahmen/Gekachelte Rahmen* kann man die Bilder auch nebeneinander anzeigen.

Bei einer Reihe von AIRTOOLS-Programmen wird der Nutzer aufgefordert, im Bild Regionen zu definieren, z.B. für die ausgedehnte Koma des Kometen oder für Bereiche des Hintergrunds, die in den folgenden Meßroutinen verwendet werden. Da Regionen mehrmals benötigt werden, empfiehlt es sich, in der oberen der zwei Knopfleisten über dem Bild *region* zu wählen, damit in der unteren Leiste bestimmte Aktionen für Regionen schneller zugänglich sind. Folgende Dinge sollten geübt werden:

-   Regionen anlegen durch Klicken (bzw. Klicken und Ziehen) mit der linken Maustaste im Bild. Dies erzeugt standardmäßig eine Kreisregion. Andere Formen können über den Menüpunkt *Region/Form* gewählt werden.
-   Eine Region wird durch einen Mausklick innerhalb der Fläche zur Bearbeitung markiert. Sie kann nun durch Klicken und Ziehen an den Markierungspunkten modifiziert werden. Bei einer Polygon-Region können Punkte durch Klicken auf den Linien hinzugefügt und mit Hilfe der Entf-Taste gelöscht werden. Dabei ist darauf zu achten, daß der Mauszeiger genau über einem Punkt steht. Nur so wird dieser allein gelöscht, ansonsten die gesamte Region.
-   Mehrere markierte Regionen werden gleichzeitig bewegt, kopiert (Strg-C, Strg-V) oder gelöscht.
-   Regionen speichern, z.B. unter Verwendung der Knopfleisten oberhalb des Bildes (obere Leiste: *region*, untere Leiste rechts: *speichern*) oder Verwendung des Menüpunktes *Region/Regionen* speichern. Alle Regionen sind stets im voreingestellten Format (Format: ds9, Koordinatensystem: physical) abzuspeichern.

AIRTOOLS Tasks im Überblick
---------------------------

Die Bearbeitung und Analyse der Kometenaufnahmen erfolgt in mehreren Schritten, die nacheinander auszuführen sind. Sie sind als Tasks unter dem Menü *Analyse* eingebunden. Durch Drücken der Taste F1 bei Positionierung des Mauszeigers im Bildbereich erhält man jederzeit eine Übersicht zu den vorhandenen AIRTOOLS Tasks (und Hilfsprogrammen) und deren Tastenkürzel.

Die Bearbeitungsschritte sind

-   Astrometrische Kalibration des Sternenstacks
-   Entfernung des Hintergrundgradients in beiden Stacks
-   Extraktion der PSF im Sternenstack und im Kometenstack (Sternspur)
-   Kometenextraktion
-   Manuelle Erfassung von Zusatzinformationen
-   Fotometrische Kalibration

Beim Start eines Tasks werden in einem einfachen Formular Parameter abgefragt, wobei in den meisten Fällen bereits die Voreinstellungen zu guten Ergebnissen führen. Während ein Task läuft, werden Meldungen und diverse Zwischenergebnisse in einem Fenster angezeigt und gleichzeitig in eine Protokolldatei `airtask.log` im Projektordner geschrieben. Im Meldungsfenster erscheinen gegebenenfalls auch Aufforderungen zu Aktionen des Nutzers.

Verschiedene Tasks erzeugen neue Ergebnisbilder, die dem Hauptfenster *SAOImage AIRTOOLS* hinzugefügt werden. Manche Tasks erzeugen temporär auch neue SAOImage Fenster, die am Namen in der Titelleiste des Fensters unterscheidbar sind. Diese temporären Fenster sind nach Beendigung des jeweiligen Tasks zu schließen.

Astrometrie
-----------

Erster Arbeitsschritt ist die astrometrische Kalibration des Sternenstacks. Dazu muß dieser im Bildrahmen dargestellt sein.

Vor Aufruf des Tasks ist jedoch zuerst die Bildorientierung zu überprüfen. Einige Programme, die zur Bildbearbeitung und zum Stacken verbreitet sind, benutzen eine geänderte Reihenfolge der Pixel in der FITS-Datei. Es kann also sein, daß das dargestellte Bild unter SAOImage gespiegelt erscheint, d.h. oben und unten vertauscht sind. In diesem Fall müssen Sternenstack und Kometenstack nacheinander gespiegelt werden. Die entsprechende Funktion *imflip* wird durch Taste i aufgerufen. Wenn keine Referenzaufnahme oder Sternkarte zur Hand ist, kann ein Ausschnitt des Palomar Digital Sky Survey erzeugt werden. Dazu mit Taste a die Funktion *aladindss* aufrufen, die ein Browserfenster mit einem entsprechenden Himmelsausschnitt öffnet.

Nach Bildwechsel zum Sternenstack kann die astrometrische Kalibration gestartet werden (Aufruf über entsprechenden Eintrag im Analysis-Menü oder Taste w).

Ein Fenster zur Eingabe/Modifikation der Taskparameter erscheint:

starstack:  
Bildname des Sternenstacks. Üblicherweise muß hier nichts eingegeben werden und es wird das gezeigte Bild verwendet

catalog:  
Referenzkatalog für die Astrometrie. Die Kataloge UCAC-4, UCAC-3 und PPMX stehen zur Verfügung. Letzterer kann insbesondere für Weitfeldaufnahmen mit geringerer Reichweite nützlich sein.

maglim:  
Wenn angegeben werden nur Katalogsterne verwendet, die heller als dieser Grenzwert sind.

thres:  
S/N Schwellwert für Sterne in der Aufnahme. Bei Aufnahmen in dichten Sternfeldern sollte der Wert erhöht werden, um die Zahl der zu matchenden Sterne zu begrenzen.

north:  
Näherungswert für den Positionswinkel der Richtung zum Himmelspol auf der Aufnahme. Norden oben entspricht 0° und Norden links 90°.

opts:  
Feld für Experten-Optionen (sollte nicht benutzt werden).

<img src="images/wcscalib_param.png" alt="Taskparameter Astrometrie" width="453" />

Die Kalibration nutzt Sterne der gesamten Aufnahme, nicht nur diejenigen in der Umgebung des Kometen. Vordergründig ist nicht die möglichst präzise Positionsbestimmung des Kometen, sondern eine gute Bestimmung der Koordinaten über das ganze Feld um später die Identifikation vieler fotometrischer Standardsterne zu ermöglichen.

Nach Übernahme der Taskparameter (Knopf OK) beginnt das Programm mit dem Download der Katalogsterne. Das kann in weiten bzw. sternreichen Feldern einige Zeit in Anspruch nehmen. Danach startet der Match-Algorithmus und am Ende werden Plots zur Begutachtung der Ergebnisse erzeugt und Resultate im Meldungsfenster ausgewiesen:

-   nimg - Anzahl der identifizierten Sterne im Bild
-   ncat - Anzahl der heruntergeladenen Katalogsterne (in einem Feld ca. doppelt so groß wie das Bild)
-   nmatch - Anzahl der gematchten Sterne
-   nhigh - Anzahl der gematchten Sterne mit hohem S/N
-   xrms - Mittlerer Fehler in x in Bogensekunden
-   yrms - Mittlerer Fehler in y in Bogensekunden

Zur Einschätzung der Qualität der Astrometrie werden mehrerer Plots generiert. Der zuerst erscheinende Plot zeigt die verbleibenden Positionsfehler. Durch Drücken der Leertaste im Plot gelangt man zum zweiten Plot, der die Lage des Bildfeldes im Koordinatennetz und die Variation der Pixelskala als Maß der Verzeichnung zeigt. Der dritte und letzte Plot zeigt die Sternpositionen. Die gematchten Sterne sind hier grün dargestellt.

<img src="images/wcscalib_images.png" alt="Plots zur Bewertung der Astrometrie" width="491" />

Es empfiehlt sich, den Parameter *thres* soweit zu erhöhen, daß bei einer Sensorgröße von 10 Megapixel nicht mehr als ca. 5000 Sterne in der Aufnahme detektiert werden. Ebenso sollte die Zahl der verwendeten Katalogsterne auf ein Maximum von ca. 10000 beschränkt werden, was durch das setzen von *maglim* erreicht wird. Gute Ergebnisse der Astrometrie werden bei erfolgreicher Zuordnung von ca. 1000 Sternen erzielt.

Bild-Hintergrund
----------------

Um später schwache Details im Bild besser erkennen zu können, muß der Bild-Hintergrund geebnet werden. Dabei erfolgt lediglich der Abzug eines linearen Gradienten. Die Korrektur mit Flächen höherer Ordnung bzw. mit nichtlinearen Anteilen würde unweigerlich zu systematischen Fehlern bei der Fotometrie der ausgedehnten Koma und des Hintergrundes führen.

Bestimmte Bildregionen können stark vom natürlichen Helligkeitsgradienten im Bildhintergrund abweichen (sehr helle Sterne mit großem Hof, Sternhaufen etc.). Diese sollten von der Gradientenberechnung ausgeschlossen werden. Dazu müssen sie vor Aufruf des Tasks festgelegt werden. Es ist zweckmäßig, zuerst die vollständige Aufnahme sichtbar zu machen (Menü *Zoom/Zoom Fit*) und den Kontrast stark anzuheben. Anschließend können beliebige Regionen unterschiedlicher Form erzeugt werden, die anschließend im Task nicht mit berücksichtigt werden.

Die Taskparameter sind

starstack:  
Bildname des Sternenstacks. Üblicherweise muß hier nichts eingegeben werden und es wird das gezeigte Bild verwendet.

bgmult:  
Faktor, um den die Intensitäten (ADU) im zu erzeugenden Hintergrundbild gestreckt werden. Dies ist notwendig, da an einigen Stellen im Programm mit Integer-Werten gerechnet wird und bei niedrigem Hintergrundsignal sonst Bild-Artefakte (z.B. Stufen) auftreten können. Empfehlung: bei Bildern mit Hintergrund &lt;=3000 ADU den Wert bei 10 belassen, bei &gt;3000 ADU auf 1 setzen.

Als Resultat erscheint ein neues Fenster *SAOImage Backgrounds* mit dem verkleinerten Bild der Residuen und - mit der Taste Tab erreichbar - dem Gradientenbild. Quantitative Angaben zur Amplitude des Gradienten und zum mittleren, gestreckten Helligkeitswert findet man im Meldungsfenster des Tasks.

Das Residuenbild ist gut geeignet, um die Genauigkeit der Flatfield-Korrektur zu ermitteln. Bei hoher Qualität der Flats und/oder dunklem Himmel werden selbst schwache Hintergrundstrukturen galaktischen Ursprungs deutlich sichtbar. Für quantitative Aussagen können Regionen erzeugt und vermessen werden. Dies geschieht mit Taste s, die die Funktion *regstat* aufruft.

Ermittlung der PSF
------------------

Ziel dieses Aktion ist die Ermittlung des Stern-Profils (PSF = point spread function) einerseits und des Profils der Sternspur im Kometenstack andererseits, da später alle Sternspuren aus diesem entfernt werden sollen. Es ist der Task, der die meiste Rechenzeit benötigt.

Die Taskparameter sind

set:  
Name des Image Set. Dieser sollte bereits korrekt ausgewählt sein.

starstack:  
Bildname des Sternenstacks. Üblicherweise muß hier nichts geändert werden. Es wird im weiteren Verlauf automatisch auf evtl. vorhandene Hintergrund-korrigierte Bilder zurückgegriffen.

rlim:  
Radius um den Kometen innerhalb dessen Sterne zur Erzeugung der PSF herangezogen werden. Der Radius ist in Prozent der Bilddiagonale angegeben. In den allermeisten Fällen kann die Voreinstellung verwendet werden.

merrlim:  
Bei den Iterationen zur Ermittlung der PSF werden Hintergrundsterne abgezogen. Schwache Hintergrundsterne mit einer Unsicherheit der Helligkeitsbestimmung die größer ist als der Parameterwert werden nicht berücksichtigt. Da in dichten Sternfeldern schwächere Sterne nur schwer voneinander zu trennen sind, sollten nur sicher zu erfassende, hellere Hintergrundsterne Berücksichtigung finden und entsprechend mehr Sterne ausgeschlossen werden. Das wird durch Verringerung von *merrlim* erreicht.

psfsize:  
Größe der PSF-Bilder (deren Kantenlänge) in Pixel. Die Voreinstellung ist für alle Fälle kurzer Sternspuren (respektive kurzer Kometenspur) geeignet. Die Sternspur muß letztendlich komplett in das Bild passen.

Nach Abschluß der Berechnungen wird ein Fenster *SAOImage PSF* mit den Bildern der PSF der Sterne und der Sternspur gezeigt. Diese Bilder werden mit 4-fach höherer Auflösung als die Ausgangsbilder erzeugt. Die PSF wird später nur innerhalb der dargestellten Masken verwendet. Innerhalb dieser Bereiche sollte kein Signal überlappender anderer Sterne liegen. Um dies zu erreichen ist es häufig erforderlich, einige zur Bildung der PSF verwendete Sterne manuell auszuschließen. Dazu wechselt man zum Hauptfenster und analysiert das neu dargestellte Bild in dem die Hintergrundsterne abgezogen sind und die PSF-Sterne durch Kreis-Regionen (grün) dargestellt werden.

Um einen Stern als unbrauchbar zu kennzeichnen, muß dessen Region angeklickt und markiert werden. Zum Ein- bzw. Ausschalten der Markierung (die Region wird dann rot dargestellt) dient die Taste o. Nach folgenden Kriterien findet man - mit etwas Übung - die auszuschließenden Sterne:

-   In unmittelbarer Nähe befindet sich ein heller, gesättigter und daher nicht abgezogener Stern.
-   Ein weiterer PSF-Stern steht in der Nähe und zwar so, daß beide Sternspuren überlappen bzw. dicht nebeneinander liegen.
-   Doppelsterne sind jetzt leicht erkennbar und sollten ebenfalls ausgeschlossen werden.

Nach Setzen der Markierungen und Schließen des Fensters *SAOImage PSF* muß der Task erneut aufgerufen werden. Dieses Verfahren kann mehrmals durchlaufen werden bis eine zufriedenstellende PSF erhalten wird.

Unter Umständen kann es erforderlich sein, die PSF-Masken zu modifizieren. Nach Anpassung einer Masken-Region muß diese im Unterordner `comets` gespeichert werden.

<img src="images/psfextract_images2.png" alt="PSF von Stern und Sternspur" width="453" />

Kometen-Extraktion
------------------

Die Kometen-Extraktion ist das Kernstück zu einer erfolgreichen Bestimmung der Koma-Helligkeit. Die Liste der Taskparameter ist überschaubar und nur selten sind Änderungen vorzunehmen:

set:  
Name des *Image Sets*. Dieser sollte bereits korrekt ausgewählt sein.

starstack:  
Bildname des Sternenstacks. Üblicherweise muß hier nichts geändert werden. Es wird im weiteren Verlauf automatisch auf evtl. vorhandene Hintergrund-korrigierte Bilder zurückgegriffen.

bgimage:  
Name des in der Intensität skalierten Hintergrundbildes. Wenn bei der Hintergrundbestimmung (siehe [oben](#bild-hintergrund)) für bgmult 1 benutzt wurde, so muß im Dateinamen der String `bgm10` durch `bgm1` ersetzt werden.

comult:  
Faktor zur Kontraststeigerung des extrahierten Kometen-Bildes. Bei Kometen mit sehr hellem Kern ist sicherzustellen, daß bei der Kontraststeigerung nicht der Grenzwert des 16bit Dynamikbereichs überschritten wird. Dazu muß das Intensitätsmaximums des Kernbereichs im Kometenstack gemessen werden. Liegt die Intensität dort weniger als 6000 ADU über dem Hintergrund, so kann comult=10 benutzt werden. Ist die Intensität größer, muß comult=1 gesetzt werden.

Kurze Zeit nach Start der Berechnungen wird ein Fenster *SAOImage CometRegions* geöffnet. Im dargestellten Bild sind alle Sternspuren (der nicht gesättigten Sterne) abgezogen. Es ist zusätzlich geglättet, wodurch bei Erhöhung des Kontrastes und Zoomen auf niedrige Auflösung die Ausdehnung der äußeren Koma gut erfaßt werden kann. Im Meldungsfenster erscheint die Aufforderung zur Festlegung diverser Regionen mit den zu benutzenden Dateinamen.

Der Ort des Kometen (laut Ephemeriden) ist bereits durch eine Region markiert, die nun in Größe und Form der Ausdehnung der Koma angepaßt werden muß. Danach ist die Region zu speichern. Anschließend definiert man ca. 4-6 um den Kometen platzierte Regionen zur Messung des Hintergrundes und speichert diese ebenfalls. Liegen im Bereich der Koma Spuren von gesättigten Sternen, so müssen diese Regionen ebenfalls erfasst und gespeichert werden, damit sie bei der später erfolgenden Fotometrie ausgeschlossen werden.

Nach dem Schließen des Fensters *SAOImage CometRegions* wird die Analyse fortgesetzt. Dabei wird u.a. aus dem extrahierten Kometen und den Aufnahmezeiten der gestackten Einzelaufnahmen eine Kometenspur modelliert. Wurden bei der Erfassung der Daten des *Image Sets* im Launcher die Einzelbilder nicht angegeben, so können nur Schätzungen der Aufnahmezeiten verwendet werden. Die modellierte Kometenspur ist dann weniger genau.

Der Abzug von Sternen bzw. Sternspuren basiert auf der Verwendung fotometrischer Daten, die im Sternenstack durch ein schnelles Verfahren gemessen werden. Dabei treten unter Umständen Ungenauigkeiten auf und es verbleiben bei einigen Sternen größere Residuen mit positivem oder negativem Signal. Schwache Sterne werden mitunter gar nicht berücksichtigt. Deshalb gibt es im nächsten Schritt die Möglichkeit, ausgewählte Sterne noch einmal genauer zu vermessen. Dazu dient das Fenster *SAOImage PhotCorr*, in dem zwei Bilder enthalten sind. Das erste zeigt den Sternenstack und die im letzten Schritt definierten Regionen. Das zweite zeigt den gleichen Sternenstack nach Abzug der Sterne und der modellierten Kometenspur. In diesem zweiten Bild können jetzt Kreisregionen auf die Sterne gesetzt werden, die neu gemessen werden sollen. Die Regionen sind in der Datei `x.newphot.reg` im Projektordner zu speichern. Danach kann das Fenster geschlossen werden.

Der weitere Fortschritt des Tasks kann in dessen Meldungsfenster verfolgt werden. Am Ende werden die Ergebnisse der Intensitätsmessungen in einer Zeile zusammengefaßt:

-   Name des *Image Sets*.
-   Mittlere Intensität in der Kometenregion in ADU
-   Fläche der Kometenregion
-   Gesamtintensität des Kometen in ADU
-   Durchmesser des Kometen in Pixel (bei flächengleichem Kreis)
-   interner Hintergrundwert
-   Variation des Hintergrundes (Statistik der verschiedenen Hintergrundregionen)

<img src="images/cometextract_results.png" alt="Messergebnisse nach Kometenextraktion" width="453" />

Im Hauptfenster wird eine Reihe von Bildern zur Begutachtung der Kometenextraktion hinzugefügt:

-   Extrahierter Komet, d.h. Kometenstack nach Abzug der Sternspuren
-   Geglättetes Bild des Kometen mit den zur Messung benutzten Regionen
-   Sternenstack nach Abzug der Sterne
-   Sternenstack nach Abzug von Sternen und Kometenspur mit Kennzeichnung der nachgemessenen Sterne

Unter Umständen ist es sinnvoll, Anpassungen an den Meßregionen vorzunehmen. Beispiesweise kann es wünschenswert sein, die Kometenregion noch einmal zu vergrößern. Nach speichern der modifizierten Region mit korrektem Dateinamen muß dann der Task erneut gestartet werden.

Manuelle Messungen
------------------

Dieser Task dient zur Erfassung von weiteren Meßdaten. Folgende Zusatzmessungen können manuell auf den im Hauptfenster dargestellten Bildern durchgeführt werden:

-   Messung der Intensität von Cosmics im Bereich der Komaregion. Die Summe der Counts stellt eine negative Korrektur zur Gesamtintensität der Koma dar.
-   Abschätzung der fehlenden Intensität von “Löchern” in der Koma, die von den Bereichen der gesättigten Sterne herrühren (positive Korrektur).
-   Messung der Intensität der schwächsten, gerade noch wahrnehmbaren Sterne zur späteren Ermittlung der Grenzhelligkeit der Aufnahme
-   Schweifparameter wie Länge und Winkel, die mittels *Region/Form/Vektor* im Bild gemessen werden können

Die ermittelten Größen werden in den entsprechenden Feldern als Taskparameter eingetragen und in die weitere Auswertung mit einbezogen.

Fotometrie
----------

Um die gemessenen Intensitäten in Helligkeiten umzuwandeln, ist eine fotometrische Kalibration notwendig. Dazu werden Referenzsterne aus einem Katalog in der Aufnahme des Sternenstacks identifiziert und klassisch mit dem Verfahren der Aperturfotometrie gemessen.

Hier ist die Beschreibung der Taskparameter:

set:  
Name des *Image Sets*. Dieser sollte bereits korrekt ausgewählt sein.

idx:  
Bei Verwendung von Aufnahmen mit mehreren Farbkanälen (RGB Bilder) ist hier die Nummer des Kanals (bzw. der Bildebene oder der FITS Extension) anzugeben. Der Grünkanal eines RGB Bildes hat beispielsweise idx=2.

catalog:  
Name des fotometrischen Referenzkatalogs. Die Kataloge APASS und Tycho2 sind verfügbar.

color:  
Farbgleichung, d.h. Farbband und Farbindex des Referenzkatalogs, die in die Ausgleichsrechnung einbezogen werden.

aprad:  
Aperturradius, der zur Messung in der Aufnahme benutzt wird. Dieser wird normalerweise automatisch ermittelt (u.a. aus FWHM abgeleitet). In dichten Sternfeldern oder bei defokussierten Aufnahmen kann es sinnvoll sein, abweichend einen selbstdefinierten kleineren Wert zu setzen.

topts:  
Optionen, die für Kalibration mit Sternen des Tycho2-Katalogs verwendet werden. Folgende Optionen stehen zur Verfügung:

-   `-l <wert>` - Helligkeitslimit, d.h. begrenze auf Sterne heller als <wert>, Standard: unbegrenzt
-   `-n <wert>` - Anzahl der Sterne, beginnend bei den hellsten Sternen, Standard: 100
-   `-r <wert>` - Maximalabstand vom Kometen in Pixel, Standard: 25% der Bilddiagonale

aopts:  
Optionen, die für Kalibration mit Sternen des APASS-Katalogs verwendet werden (vgl. *topts*)

skip:  
Liste von Sternen, die beim Fit ausgeschlossen werden (durch Leerzeichen getrennte ID’s).

Nach Übernahme der Parameter beginnt das Programm mit dem Download der Katalogsterne und dem Match-Algorithmus. Anschließend werden die gefundenen Sterne durch Aperturfotometrie gemessen.

Bei der Fotometrie von z.B. Veränderlichen Sternen verwendet man gleich große Aperturen für den Veränderlichen und die Vergleichssterne. Die Aperturgröße wird so gewählt, daß ein optimales Signal-Rauschverhältnis genutzt wird. Dabei spielt es keine Rolle, daß dabei ca. 20% des Sternlichts außerhalb der Apertur verbleiben, da dieser Anteil bei Veränderlichem und Vergleichsstern gleich ist. Im Falle der Kometenfotometrie ist das anders: die Kometenmessung erfolgt typischerweise in einer wesentlich größeren Region. An die Aperturmessung der Vergleichssterne ist also eine Korrektur anzubringen, deren Betrag durch Messung ausgewählter heller Sterne mit sehr viel größerer Apertur ermittelt werden kann.

Die Ergebnisse werden in zwei Plots dargestellt: der erste Plot zeigt die verbliebenen Abweichungen vom Fit und der zweite die Helligkeitskorrektur bei Verwendung großer Aperturen.

<img src="images/photcal_errorplot2.png" alt="Residuen der Fotometrie der Referenzsterne" width="340" />

Im Meldungsfenster des Tasks werden die Ergebnisse der Fotometrie zusammengefaßt. Am Ende des vorletzten Textblocks werden gegebenenfalls Hinweise zu Sternen mit großen Abweichungen gelistet (*outliers*). Wenn gewünscht, können diese von der Analyse ausgeschlossen werden. Dazu kopiert man die Liste der Identifier, ruft den Task erneut auf und fügt diese Liste im Feld *skip* ein.

Die letzte Datenzeile im Meldungsfenster entspricht einem ICQ Record, wie er für Meldungen an die ICQ oder an die COBS Datenbank verwendet wird.

In der Zeile darüber befinden sich diverse Zusatzinformation wie

-   mzero: Nullpunkt der Helligkeitsskala
-   nstar: Anzahl der in der Ausgleichsrechnung benutzten Sterne
-   rms: mittlerer Fehler der Helligkeit eines Sterns
-   moon: Phase, Winkelabstand, Höhe des Mondes
-   alt: Höhe des Kometen
-   m1: Helligkeit des Kometen
-   d: Komadurchmesser in Bogenminuten

<img src="images/photcal_results.png" alt="Ergebnisse der Kometen-Fotometrie" width="453" />

Projektsicherung
================

Bei Verwendung der AIRTOOLS mit einem Linux Live-System auf DVD oder ISO-Datei innerhalb einer virtuellen Maschine müssen die Ergebnisse vor dem Herunterfahren des Linux Systems unbedingt auf einem externen Medium gesichert werden.

Das geschieht so, wie es im Abschnitt zum [Dateiaustausch](#austausch-von-dateien-zwischen-host-und-virtualisiertem-linux-pc) beschrieben ist. Wird dabei z.B. ein Projektordner auf einen FAT-formatierten USB-Stick geschrieben, kommt es zu Fehlermeldungen beim Kopieren von symbolischen Links. Diese Links werden vom FAT-Dateisystem nicht unterstützt und müssen übersprungen werden.

Ein gesichertes Projekt kann bei Bedarf später erneut bearbeitet (oder fortgesetzt) werden. Dazu geht man wie folgt vor:

-   Starten des virtualisierten Linux-Rechners und Installation der AIRTOOLS
-   Dateimanger starten durch Doppelklick auf Icon *Persönlicher Ordner*
-   Neuen Ordner `airtools` erstellen, der als Basisordner für AIRTOOLS-Projekte dienen soll
-   Das gesicherte Projekt in diesen Basisordner kopieren
-   Start des Airtools-Launchers, Auswahl des korrekten Basisordners und ohne Eintrag eines Beobachtungsdatums mit Knopf OK fortsetzen

Das Projektformular des Launchers wird erneut gestartet mit dem Unterschied, daß im Basisordner erkannte, schon existierende Projekte aufgenommen werden. Diese sind jetzt über die oberen Auswahllisten (z.B. *All projects*) selektierbar.

Nach der Auswahl des vorhandenen Projekts und Übernahme des Formulars mit OK erscheint das Formular *Image Set*. Dort kann ein bereits definiertes Set ausgewählt werden. Schließlich gelangt man zum letzten Formular *Launch AIRTOOLS* und startet die Bearbeitung mit den AIRTOOLS unter Verwendung der bereits vorhandenen, konvertierten Bilder von Sternenstack und Kometenstack. Eine Kurzübersicht über alle definierten Sets und gegebenenfalls bereits vorhandene fotometrische Ergebnisse erhält man mittels Taste q.

Anhang
======

Dateien im Projektordner
------------------------

Die verschiedenen AIRTOOLS Tasks erzeugen eine Reihe von Dateien und Ordnern im Projektverzeichnis, die es erlauben, auch später alle Arbeitsschritte nachzuvollziehen und Zwischenergebnisse zu analysieren.

Im Projektverzeichnis befinden sich folgende Textdateien mit Metadaten

-   `camera.dat`: Angaben zu verwendeten Instrumenten (Teleskop und Kamera, siehe [oben](#formular-new-instrument))
-   `refcat.dat`: Informationen zu Referenzkatalogen für interne Zwecke
-   `set.dat`: Angaben zu den Beobachtungen (Image Sets, siehe [oben](#formular-image-set))
-   `sites.dat`: Angaben zu Beobachtungsorten (siehe [oben](#formular-new-site))
-   `rawfiles.dat`: Angaben zu den Einzelbelichtungen

Nach Abschluß aller Arbeiten existieren zu jeder Kometenbeobachtung eine Reihe von Bilddateien (Endung `pgm` oder `ppm`) und Headerdateien (Endung `head`), die mit dem Namen des Sets beginnen. Heißt das Image Set co01 so beginnen alle Dateien die sich auf den Sternenstack beziehen mit `co01.`, alle Dateien die vom Kometenstack abgeleitet sind mit `co01_m.`. Taucht im Namen die Zeichenkette `bgs` auf, so handelt es sich um ein Bild, dessen Hintergrundgradient abgezogen wurde.

Bei späteren Recherchen oder auch bei der Fehlersuche ist die Logdatei `airtask.log` von besonderem Interesse. Hier sind alle Ausgaben der AIRTOOLS Tasks, die in den zugehörigen Meldungsfenstern erschienen sind, protokolliert.

Die Tasks erzeugen Unterorner mit folgenden Informationen:

-   Verzeichnis **wcs** enthält Dateien und Plots der astrometrischen Kalibration
-   Verzeichnis **bgcorr** enthält Dateien im Zusammenhang mit der Hintergrundkorrektur
-   Verzeichnis **comet** enthält u.a. die extrahierten PSF Bilder und die Regionen von Komet und Hintergrund
-   Verzeichnis **phot** enthält Dateien die bei der photometrischen Kalibration entstehen

Dateien im Projektordner, deren Namen mit `x.` beginnen, enthalten temporäre Informationen, die nach dem Abschluß der Arbeiten nicht mehr benötigt werden.

Xubuntu Linux - Erste Schritte
------------------------------

Der Desktop besitzt oben eine dunkle Zeile (*Panel*) mit diversen Symbolen: ganz links das blau-weiße Symbol zum Öffnen des Programm-Menüs und rechts die Statusanzeigen für Stromversorgung, Netzwerk, Lautstärke und Datum/Zeit. Das geöffnete Programm-Menü enthält unten rechts Symbole zum Start des Einstellungs-Managers, zum Sperren des Bildschirms und zum Herunterfahren des Linux-Systems.

Auf dem Desktop befinden sich drei Symbole. Durch Doppelklick auf eines dieser Symbole wird die Dateiverwaltung (Dateimanager *Thunar*) gestartet. Der *Persönliche Ordner* ist dabei das Pendant zu *Eigene Dateien* unter Windows. Im Unterschied zu Windows-Systemen werden Pfadangaben unter Linux durch einen Schrägstrich “/” voneinander getrennt. Das Dateisystem ist hierarchisch aufgebaut, beginnend beim Wurzelverzeichnis (Root: `/`). Auch externe Datenträger werden als Pfade innerhalb dieser Struktur angesprochen. Wechseldatenträger erscheinen immer unterhalb von `/media`. Alle Nutzerverzeichnisse befinden sich unterhalb von `/home`.

Als einfacher Texteditor (ähnlich zu Notepad) ist unter Xubuntu *Mousepad* vorinstalliert. Als Standard Webbrowser wird *Firefox* verwendet. Ein einfacher Taskmanager kann im Programmmenü unter der Rubrik System aufgerufen werden.

Links:

-   Offizielle Xubuntu Seite <https://xubuntu.org>
-   Ubuntuusers Wiki <https://wiki.ubuntuusers.de>: Sehr umfangreiche deutschsprachige Hilfe zu allen Themen rund um Ubuntu und dessen Linux-Anwendungen. Auch Xubuntu (<https://wiki.ubuntuusers.de/Xubuntu/>) wird in einem Überblick behandelt.

<!--
  AIRTOOLS Demo unter <https://www.youtube.com/watch?v=sK9D_M06ovA>.
  Das Video bezieht sich auf eine etwas ältere Programmversion (Mai 2016), die
  wesentlichen Arbeitsschritte sind aber unverändert geblieben
-->
Installation von Xubuntu Linux in VirtualBox VM
-----------------------------------------------

Die permanente Installation von Xubuntu Linux auf eine virtuelle Festplatte innerhalb einer VirtualBox VM ist nicht kompliziert und dauert ca. 10-15 Minuten. Das installierte Linux-System kann den persönlichen Bedürfnissen angepasst werden und alle Modifikationen bleiben erhalten. Somit ist auch die AIRTOOLS Installation nur einmal vorzunehmen und alle Programme sind nach jedem Start der VM sofort verfügbar.

Desweiteren wird in einem so installierten System der gesamte Speicher der der VM zugewiesen ist, als RAM verwendet. Neue bzw. modifizierte Dateien werden auf der virtuellen Festplatte abgelegt und sind permanent. Der virtualisierte Rechner verhält sich jetzt vollständig analog zu einem realen System.

Zur Vorbereitung ist die Erzeugung einer virtuellen Festplatte notwendig. Das geschieht auf folgende Weise:

-   Oracle VM VirtualBox Manager starten
-   Virtuelle Maschine mit xubuntu ISO wählen, Werkzeug *Ändern*, Reiter Massenspeicher
-   *Controller: SATA* anklicken, kleines Festplatten-Icon (mit grünem Plus) klicken und im Dialog den Knopf “Neue Platte erzeugen” klicken
-   Ordner mit ausreichend Platz wählen und Dateiname angeben
-   Größe der virtuellen Platte mindestens 10 GB, empfohlen 20 GB oder größer, wenn genug Platz vorhanden ist; Typ VDI, dynamisch, dann Knopf “Erzeugen”
-   Einstellungen mit Knopf “OK” übernehmen

Die Installation von Xubuntu Linux erfordert folgende Schritte:

-   VM starten, Fenster *Install*, Sprache Deutsch, Knopf “Xubuntu installieren”
-   Punkt *Herunterladen der Aktualisierungen* anhaken, Knopf “Weiter”
-   Installationsart: *Festplatte löschen und Xubuntu installieren* (Standard)
-   Zeitzone (Berlin) und Tastaturbelegung (Deutsch) übernehmen
-   Eingabe von Nutzernamen und Passwörtern:
    -   Ihr Name: Vorname Nachname
    -   Name Ihres Rechners: z.B. xubuntu-vm
    -   Benutzername: beliebig
    -   Passwort abfragen oder Automatisch anmelden, Daten nicht verschlüsseln
-   nach Weiter startet Installation: &lt;5min
-   Aufforderung zum Neustart befolgen
-   ISO Datei von IDE Controller der VM entfernen

Wenn keine automatische Anmeldung gewählt wurde, erscheint nach dem Booten der Login-Bildschirm. Nach Eingabe von Benutzername und Passwort wird der Nutzer angemeldet und der Desktop erscheint. Die [Installation der AIRTOOLS](#installation-der-airtools-software) kann beginnen.
