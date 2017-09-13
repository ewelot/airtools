
<!-- begin of comments ----
# convert to pdf:
pandoc --toc -N -V lang:german -V geometry:margin=4cm \
    manual-de.md -o test.pdf
---- end of comments -->


---
title: 'Anleitung zur Kometen-Fotometrie mit AIRTOOLS'
author: Thomas Lehmann
---

\newpage

# Einführung

AIRTOOLS ist ein Akronym für "Astronomical Image Reduction TOOLSet" und steht
für eine Sammlung von Programmen zur Verarbeitung von astronomischen Bilddaten,
die mit CCD oder Digitalkamera aufgenommen wurden. Die Software bietet
Funktionen zur grundlegenden Bildbearbeitung (z.B. RAW-Entwicklung,
Bias-, Dark-, Flat-Korrektion), zur automatischen Objekterkennung und zum
Registrieren und Stacken von Bildserien sowie zur Astrometrie und Fotometrie
unter Verwendung verschiedener Referenzkataloge.

Darüber hinaus existieren spezialisierte Tools zur Auswertung von
Kometen-Aufnahmen. Diese haben das Ziel, eine zur visuellen
Gesamthelligkeitsbestimmung adäquate Fotometrie zu ermöglichen - mit den
Vorteilen von Reproduzierbarkeit, hoher Reichweite und unter Ausschluß von
subjektiven Fehlern und Differenzen zwischen Beobachtern.   

Die AIRTOOLS Software benötigt ein Linux-Betriebssystem. Dies muß aber nicht
zwingend auf dem Rechner des Anwenders installiert sein, sondern kann entweder
in einer virtuellen Umgebung laufen oder von einem Linux Live-System (d.h. von
einem bootbaren DVD- bzw. USB-Medium oder einer ISO-Imagedatei) gestartet
werden.

Die einzelnen Programme sind vollständig als Kommandozeilen-Programme
einsetzbar und somit in Skripten gut kombinierbar. Die wesentlichen Werkzeuge
zur Kometen-Fotometrie sind zur leichteren Handhabung über ein grafisches
Nutzerinterface bedienbar. Die Erläuterung ausschließlich jener Werkzeuge
ist Gegenstand dieser Anleitung.

Die AIRTOOLS Programmsammlung verwendet eine ganze Reihe von Programmen
die Bestandteil der meisten Linux Distributionen sind, wie z.B. ImageMagick,
GraphicsMagick, Netpbm und Gnuplot. Außerdem werden frei verfügbare,
leistungsfähige Programme aus dem Umfeld der professionellen
Astro-Bildverarbeitung benutzt. Das sind insbesondere

- [SAOImage DS9](http://ds9.si.edu/site/Home.html): Image display, catalog
  viewer and analysis GUI
- [Astromatic Software](http://www.astromatic.net) by E. Bertin: Automatic source
  detection (sextractor), astrometric calibration (scamp), stacking (swarp),
  modeling (skymaker) and more
- [Stilts](http://www.starlink.ac.uk/stilts/) by M. Taylor: Powerful table
  processing
- [WCSTools](http://tdc-www.harvard.edu/software/wcstools/) by J. Mink:
  Utilities to create and manipulate the world coordinate system of images


Die AIRTOOLS Software ist frei verfügbar. Der Quellcode ist auf der
[Projektseite](https://github.com/ewelot/airtools) zu finden. Leicht
installierbare Programmpakete werden für ausgewählte Linux Distributionen zur
Verfügung gestellt.

Für Anregungen, Fragen oder einfach nur Feedback zu Programm oder Anleitung
erreichen Sie mich unter: <t_lehmann@freenet.de>

Viel Erfolg!

Thomas Lehmann

Weimar, im September 2017



# Kometen-Aufnahmen

Sollen Aufnahmen zur späteren Kometen-Fotometrie gewonnen werden, empfielt es
sich, anstatt einer langen Belichtung mehrere kürzere Belichtungen als Serie
aufzunehmen. Da die Größe der Koma zumeist weit unterschätzt wird, sollte
auf ein ausreichend großes Gesichtsfeld geachtet werden. Es sollten möglichst
wenige gesättigte Sterne in den Bereich der Koma fallen.

Zur Trennung von Komet und Hintergrundsternen
werden zwei Bilddateien benötigt: zum einen das auf den Kometen gestackte Bild,
das die Sterne als Spuren enthält (im folgenden: Kometen-Stack) und zum zweiten
das auf die Sterne gestackte Bild, das die Kometenspur zeigt (Sternen-Stack).

Die Bildkalibration unter Verwendung von Bias, Dark, Flat mit den Mittels der
AIRTOOLS wird an dieser Stelle nicht beschrieben, ebensowenig das Stacken der
Einzelbilder. Dazu existieren auch unter den zumeist benutzten Betriebssystemen
Windows und MacOS ausgereifte Programme, die den meisten Astrofotografen
geläufig sind. Um die so entstandenen gestackten Bilder mit den AIRTOOLS
weiter bearbeiten zu können, sind folgende Voraussetzungen zu erfüllen:

- die Dateien liegen im FITS-Format vor
- die Linearität des mit dem Detektor empfangenen Signals muß erhalten bleiben
- es sollte kein Abzug des Hintergrundsignals erfolgen, auch keine Ebnung,
  d.h. ein natürlicher Helligkeitsgradient des Himmels soll in der Aufnahme
  erhalten bleiben
- der Intensitäts-Nullpunkt ("Schwarzpunkt", d.h. die Counts ohne Lichteinfall)
  muß bekannt sein (idealerweise bei 0)
- die Stacks sind aus Mittelwert-Bildung entstanden, d.h. die Counts im Stack
  haben in etwa den ADU-Wert wie er im (Roh-) Einzelbild nach Bias-Abzug
  gemessen wird
- die Beobachtungszeit (idealerweise Mitte) ist im FITS-Header enthalten (JD
  oder DATE-OBS in UT)



# Installation

Im Folgenden wird die Installation der AIRTOOLS für Nutzer beschrieben, die
einen PC mit Windows oder MacOS Betriebssystem besitzen. Im ersten Teil wird
dabei ein virtualisiertes Linux-System gestartet. Nutzer, die bereits
einen Linux-Rechner betreiben, können dieses Unterkapitel 3.1
überspringen. Im zweiten Teil wird die eigentliche AIRTOOLS-Installation
im (eventuell virtualisierten) Linux-System beschrieben.

Die Hardware-Voraussetzungen zum Arbeiten mit den AIRTOOLS sind nicht hoch.
Jeder PC oder Laptop, der in den letzten ca. 7 Jahren angeschafft wurde, ist
dazu geeignet. Allerdings ist ein großer Bildschirm,
wie bei allen Programmen der Bildbearbeitung, von Vorteil.

Ein Internet-Anschluß ist zwingend erforderlich, da diverse Daten wie
Ephemeriden und astrometrische und fotometrische Referenzkataloge online
abgefragt werden.



## Vorbereitung eines Rechners mit Windows oder MacOS Betriebssystem

Ein virtualisierter PC - auch virtuelle Machine oder kurz VM genannt - ist eine
ideale Lösung, um eine von den Daten und Programmen des eigentlichen Rechners
(Host) abgesetzte, isolierte Umgebung zu schaffen in der beliebige
Betriebssysteme und Anwendungen laufen. Es ist auch möglich, mehrere VMs
gemeinsam produktiv parallel zum Host zu benutzen - gerade so, als ob man
mehrere Rechner in einem Netzwerk betreiben würde.

Um die AIRTOOLS auf einem virtualisierten Linux-PC installieren zu können
benötigt man eine Virtualisierungs-Software, die auf dem Host-PC installiert
wird und ein Linux Installations-Medium (z.B. als DVD oder ISO-Datei).

### VirtualBox

[VirtualBox](http://www.virtualbox.org) ist eine ausgereifte, frei erhältliche
Virtualisierungs-Software. Sie müssen die zu Ihrem (Host-) Betriebssystem
passende Version von der Download-Seite herunterladen und installieren. Für
ein angenehmes Arbeiten empfehle es sich, das ebenfalls auf der
Download-Seite angebotene "VirtualBox Extension Pack" herunterzuladen und zu
installieren: VirtualBox Manager starten, Menüpunkt Datei/Einstellungen,
Zusatzpakete, Paket hinzufügen und die heruntergeladene Datei auswählen.

### Linux Installations-Medium

Linux gibt es in sehr unterschiedlichen Ausprägungen, wobei das Betriebssystem
und ein großer Teil von Anwendungssoftware gebündelt als sogenannte Distribution
angeboten wird. Prinzipiell lässt sich die AIRTOOLS-Software auf einer
beliebigen Linux-Distribution installieren, da alle benötigten Komponenten
auch im Quellcode verfügbar sind. Um jedoch den Installationsaufwand zu
minimieren, empfehle ich die Verwendung einer Linux-Version, für die alle
Programme als Binärpakete verfügbar sind (sie sind somit kompiliert und leicht
installierbar bzw. deinstallierbar). Dies sind zur Zeit die 64bit Versionen von

- Ubuntu 16.04 (und Varianten wie XUbuntu)
- Debian 8

In der weiteren Anleitung wird [XUbuntu Linux](https://xubuntu.org/) in der
Version 16.04 LTS (64bit) verwendet. Sie müssen die entsprechende ISO-Image
Datei aus dem Download-Bereich herunterladen (aktuell z.B.
[xubuntu-16.04.3-desktop-amd64.iso](http://ftp.uni-kl.de/pub/linux/ubuntu-dvd/xubuntu/releases/16.04/release/xubuntu-16.04.3-desktop-amd64.iso)).

### Linux Live-System als VirtualBox VM

Die meisten (großen) Linux-Distributionen bieten ihre Software mittlerweise als
Live-System an, d.h. das Betriebssystem und die Anwendungen befinden sich auf
einem bootbaren Medium. Das System kann beliebig getestet werden und bei Bedarf
aus dem gebooteten Zustand heraus installiert werden.

So funktioniert das auch mit der XUbuntu ISO-Datei, die in einer VirtualBox VM
direkt als Bootmedium verwendet werden kann - genauso wie eine aus der
ISO-Datei erstellte DVD. Dazu sind folgende Schritte notwendig:

- Oracle VM VirtualBox Manager starten
- Erzeugung einer neuen VM
    - Werkzeugleiste "Neu"
    - Name: XUbuntu-16.04, Typ: Linux, Version: Ubuntu (64bit)
    - Speicher: ca. Hälfte des RAM vom Hostsystem, mind. 2000 MB
    - Platte: keine Festplatte
    
- Einstellungen der VM vornehmen
    - Werkzeugleiste "Ändern"
    - unter "System" zu Tab Prozessor: Anzahl auf Hälfte der CPUs des
      Hostsystems erhöhen
    - unter "Anzeige" zu Tab Bildschirm: Grafikspeicher auf 32 MB erhöhen
    - unter "USB" kann USB-3.0-Controller aktiviert werden
    
- ISO-Datei als Bootmedium "einlegen"
    - unter "Massenspeicher", Controller IDE auf "CD leer" klicken
    - über das CD-Symbol ganz rechts am Fensterrand die Auswahlliste öffnen und
      darin den ersten Eintrag "Datei für optisches Medium auswählen" wählen
    - im Dateimanager die XUbuntu ISO-Datei auswählen
    - der ISO-Dateiname erscheint dann unter Controller: IDE neben dem CD Symbol
    - das Einstellungen-Fenster mit "OK" schließen

- Virtuelles Linux System booten
    - Werkzeugleiste "Starten" beginnt den Bootvorgang des XUbuntu Linux in der
      virtuellen Maschine
    - nach einiger Zeit erscheint das Fenster "Install" in dem links als
      Sprache "Deutsch" gewählt werden kann (2 Einträge über English)
    - danach "Xubuntu ausprobieren" wählen
    - der Bootvorgang wird abgeschlossen und der XUbuntu-Linux Desktop
      erscheint

Eine Kurzanleitung zum XUbuntu Desktop befindet sich im Anhang (**EDIT**).
Das virtuelle Linux-System wird heruntergefahren durch (**EDIT**).


Das Live Linux-System ist voll funktionsfähig. Es läuft
komplett im RAM des Hosts, wobei die in der VM-Konfiguration angegebene
Speichergröße zu gleichen Teilen als RAM für Betriebssystem und Anwendungen
und als "Plattenplatz" zur Verfügung steht. D.h. bei 2 GB zugewiesenem VM
Speicher können maximal 1 GB für neue/geänderte Dateien benutzt werden. Dazu
zählen neu installierte Anwendungen und Nutzerdaten in gleicher Weise.

Alle Änderungen, die nun am Linux-System vorgenommen werden (inclusive aller neu
angelegter Dateien) sind nur solange existent, wie das System läuft - sie
befinden sich ja im RAM. Nach jedem Booten eines Live-Systems in einer VM hat
man den exakt gleichen Ausgangszustand. Das hat den Vorteil, daß das Linux
Live-System auf keine Weise unbrauchbar gemacht werden kann. Man hat eine
ideale Testumgebung für Anwendungen und Spielwiese für eigene Experimente.
Nachteile der Nutzung der AIRTOOLS in solch einem Live-System sind:

- wenig Platz für eigene Dateien
- alle Ergebnisse müssen auf ein externes Medium (z.B. USB-Platte)
  gesichert werden, bevor das virtuelle Linux-System heruntergefahren wird
- nach jedem Bootvorgang ist die AIRTOOLS Installation, die im folgenden
  Abschnitt beschrieben wird, zu wiederholen

Abhilfe für alle genannten Punkte schafft man durch die permanente
Installation des XUbuntu-Linux Systems auf eine virtuelle Festplatte innerhalb
der VM (siehe Anhang **EDIT**). Für erste Schritte und Tests der AIRTOOLS
Software ist die Arbeit mit dem Live-System hingegen bestens geeignet.

### Austausch von Dateien zwischen Host und virtualisiertem Linux PC

**EDIT**

## Installation der AIRTOOLS Software

Die hier beschriebene Installation von Binärpaketen erfordert ein laufendes
Linux-System (z.B. XUbuntu 16.04). In diesem Linux-System sind folgende
Arbeitsschritte erforderlich:

- Download des [Installationsprogramms](https://github.com/ewelot/airtools/raw/master/install_deb.sh)
  mit dem Webbrowser Firefox
- Datei-Browser öffnen (Doppelklick auf Home-Icon) und in das Verzeichnis
  wechseln, in dem das Installationsprogramm abgelegt wurde (standardmäßig
  ist es das Verzeichnis "Downloads" im "Persönlichen Ordner" des Nutzers
  xubuntu)
- Terminalfenster öffnen (im Datei-Browser unter Menu "Datei")
- Installationsvorgabg starten durch Eingabe eines Kommandos im Terminal
  sudo bash install_deb.sh

Nach dem Download der Softwarekomponenten aus dem Internet und erfolgreicher
Installation erscheint ein neues Desktop-Icon mit Namen "Airtools".
 

# Der Airtools - Launcher

Zu den für die Auswertung benötigten Daten gehören neben den
gestackten Bildern (Kometen-Stack, Sternen-Stack) diverse Informationen
mit Zusatzangaben zu den Aufnahmen, zum Beobachtungsinstrument und Aufnahmeort.
Zur Einrichtung eines neuen AIRTOOLS-Projektes und zur Abfrage der benötigten
Metadaten wird ein Hilfsprogramm, der Airtools-Launcher verwendet. Starten Sie
den Launcher durch Doppelklick auf das Airtools-Icon.

## Formular "Project"

Der obere Teil des Formulars dient zum Öffnen eines schon vorhandenen Projektes.
Soll ein neues Projekt angelegt werden, so sind die unteren Formularfelder
auszufüllen.

- Base Directory:
  Alle AIRTOOLS-Projekte werden unterhalb eines Basis-Ordners angelegt. Dieses
  Verzeichnis sollte sich daher auf einer Festplatte (bzw. Partition) mit
  ausreichend freiem Speicherplatz befinden.
- Date of observation:
  Ein Projekt kann mehrere Kometen-Beobachtungen einer Nacht enthalten, auch
  wenn diese mit unterschiedlichen Teleskopen aufgenommen wurden. Der Name des
  Projektverzeichnisses wird standardmäßig aus dem Beobachtungsdatum gebildet.
  Dabei wird das Datum zu Beginn der Nacht im Format "yymmdd" benutzt.
- Temporary Directory:
  Ordner für temporäre Dateien. Dies ist unter Linux üblicherweise /tmp.
- Observatory Site:
  Hier wird der Beobachtungsort aus einer Liste bekannter Orte ausgewählt.
  Durch Wahl von "new site" kann im nächsten Formular ein neuer Eintrag für
  einen Beobachtungsort angelegt werden.

## Formular "New Site"

## Formular "Image Set"

## Formular "New Instrument"

## Formular "Launch"



# Werkzeuge im Überblick

# Astrometrie

# Bild-Hintergrund

# Ermittlung der PSF

# Kometen-Extraktion

# Fotometrie

# Abschlußarbeiten



# Anhang


## XUbuntu Linux - Erste Hilfe

- Der Desktop
- Datei-Browser
- Text-Editor
- Web-Browser


## Installation von XUbuntu Linux in VirtualBox VM

## Einführung zu SAOImage

## Struktur der Metadaten-Dateien

