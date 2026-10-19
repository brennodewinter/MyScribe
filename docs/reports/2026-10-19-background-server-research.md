# MyScribe als achtergrondserver op een laptop: onderzoek en voorstel

Datum: 2026-10-19. Repo alleen gelezen op `main` @ 3b573b0. Niets gewijzigd, niets gedraaid tegen de echte app.

**Kern:** maak geen echte OS-service. Houd per platform een login-item per gebruiker en laat dat de launcher onzichtbaar starten (`--headless --at-login --no-browser`). Bouw daarnaast drie dingen die nu ontbreken: een nette stopdeur, een launcher die bij een crash een foutcode teruggeeft, en een installer die een draaiende server eerst stopt.

---

## 1. Huidige situatie in de code

| Wat | Waar | Feit |
|---|---|---|
| Login-item bestaat al | `scribe/autostart.py:1-33, 268-274` | Windows: waarde `MyScribe` onder HKCU `...\CurrentVersion\Run`. macOS: `~/Library/LaunchAgents/io.github.rvdbreemen.myscribe.plist`. Linux: `~/.config/autostart/myscribe.desktop`. Alles per gebruiker, zonder admin. |
| Wat het start | `autostart.py:308-318` | Release: `<launcher> --at-login --no-browser`. Op macOS: `/usr/bin/open -a <bundle> --args --at-login --no-browser`. |
| Aan/uit | Settings-kaart (TASK-089.21) en installervraag met default Nee (TASK-089.22) | Status wordt elke keer bij het OS opgevraagd. |
| Uninstall Windows | `packaging/windows/myscribe.iss:53` | `uninsdeletevalue` op de Run-waarde. Er is geen `[UninstallRun]` die een draaiende instantie stopt. Er is ook geen `AppMutex` en geen `CloseApplications`-instelling, dus Inno's default `yes` geldt. |
| Wat de gebruiker ziet bij login | `myscribe_launcher.py:2957`, `run_window` op `:2664-2710` | `--at-login` slaat alleen de first-run-vragen over. `windowed` blijft waar, dus het Tk-venster (560x360) verschijnt en moet open blijven tot Quit. TASK-089.21 legt dat expliciet vast: "the Tk window shows at login; minimising is not attempted". **Dit is het venster waar de vraag om gaat.** |
| Onzichtbare modus bestaat al | `build_release.py:83` (`--windowed`), launcher `:2884, 2957, 2200-2221` | `--headless` in een windowed build betekent: geen Tk en geen console. Het server-child draait al met `CREATE_NO_WINDOW` (`:1264-1265`) en logt naar `<home>/logs/app.log` (`:1261`). |
| Stoppen | `AppProcess.stop`, `:1289-1320` | Windows: `taskkill /T /F`, dus hard. POSIX: SIGTERM naar de groep, na 15 s SIGKILL. De app heeft geen shutdown-route (grep op `shutdown` in `scribe/` vindt alleen de phone door). |
| Wees-jobs | `supervisor.reconcile`, `scribe/supervisor.py:309ff`, aangeroepen in lifespan `scribe/app.py:254` | Een job die bij een hard stop wees raakt, wordt bij de volgende start `interrupted`. Dat vangnet werkt al. |
| Single instance | `Launch.prepare`, `:1536-1553` | Eerst een `/health`-probe, dan een bind-test op de poort. Er is geen lockfile, dus er zit een TOCTOU-venster tussen. Een tweede start opent alleen de browser. |
| Crash-signaal | `run_headless`, `:2213-2221` | Als het app-child sterft, geeft de launcher toch **exitcode 0** terug. Een supervisor (launchd, systemd, Task Scheduler) ziet dat als een nette stop en herstart dus nooit. |
| Feeds na slaap | `scribe/ingest/feeds.py:8-11` | Due-datum in plaats van countdown, dus een gemiste poll wordt na resume ingehaald. |
| GPU in het webproces | ADR-001 | Alleen het runner-child laadt modellen. Het langlevende webproces heeft geen CUDA-context, en dat is gunstig voor slaap/resume. |

**Nooit geverifieerd:**
- TASK-089.21 AC6 staat open: geen enkele echte login op enig OS heeft het item gestart, ook Windows niet.
- macOS-acceptatie 0.8.0 (`docs/reports/2026-10-03-macos-0.8.0-acceptance.md`): punt 6 (start at login) en punt 7 (uninstall) zijn niet gelopen. §5 meldt dat de first-run-vragen in het venster nooit openen.
- Linux: niemand heeft een desktop-login.

---

## 2. Per platform

De doorslaggevende randvoorwaarde staat voorop. De installer is per gebruiker zonder admin (`PrivilegesRequired=lowest`, iss:22, ADR-011). Ook de bibliotheek, `.env` en de pointer file (ADR-019) leven in het profiel van de gebruiker. Dat sluit elke echte systeemservice als default uit.

### 2.1 Windows

| Optie | Admin? | Draait als | Herstart bij crash | Valkuilen | Oordeel |
|---|---|---|---|---|---|
| **HKCU Run-waarde** (bestaat) | nee | gebruiker, sessie 1+ | nee | Max. 260 tekens (MS Learn). Windows kan Run- en Startup-items uitstellen. | **Aanbevolen** |
| Startup-map `.lnk` | nee | gebruiker | nee | Een `.lnk` maken vraagt COM. Ollama omzeilt dat door een kant-en-klare `.lnk` uit de install-dir te kopiëren (`app_windows.go`). | gelijkwaardig, geen winst |
| Task Scheduler, trigger bij aanmelden | **onzeker** | gebruiker, interactief | ja (`RestartOnFailure`) | Gevaarlijke defaults, zie hieronder. | alleen als herstart echt nodig is |
| Windows-service: WinSW v2.12.0 (2023-01, v3 alleen alpha.11), NSSM 2.24 (2014-08-31, pre-release 2.24-101 uit 2017, feitelijk onbeheerd), Servy v10.5 (2026-10-15, actief, MIT), pywin32 | **ja** | LocalSystem of serviceaccount, sessie 0 | ja | Admin nodig, ander profiel (`%LOCALAPPDATA%` van wie?), geen gebruikersschijven of mappings, CUDA in sessie 0 onzeker | **afgewezen** |

**CUDA in een service: bronnen spreken elkaar tegen.** Oude NVIDIA-forumdraden (secundair) zeggen dat CUDA op WDDM-kaarten niet uit sessie 0 werkt, alleen met TCC. Ollama's eigen docs bieden juist een NSSM-service aan met een zip die GPU-bibliotheken bevat. Dit blijft onbeslist, en het verandert de aanbeveling niet: de service valt al af op admin-rechten en het profiel.

**Task Scheduler-valkuilen** (MS Learn, schema-pagina's):
- `DisallowStartIfOnBatteries` staat standaard op true. Op een laptop op accu start de taak dan niet.
- `ExecutionTimeLimit` stopt de taak standaard na 72 uur. Zet het op `PT0S`.
- `StopIfGoingOnBatteries`: de schema-pagina spreekt zichzelf tegen (XSD `default="true"`, Remarks "default is False"). Zet het expliciet.
- `Priority` staat standaard op 7: `BELOW_NORMAL_PRIORITY_CLASS`, lage I/O- en geheugenprioriteit. Volgens "Scheduling Priorities" erft een child van een BELOW_NORMAL-ouder die klasse, dus elke runner zou geknepen transcriberen.
- Een standaardgebruiker die `schtasks /sc onlogon` uitvoert, krijgt volgens forumberichten (secundair) "access denied". XML-import met een expliciete `<UserId>` of `Register-ScheduledTask` zou werken. Dat is niet geverifieerd, en Robert is admin, dus zijn test bewijst het niet: het moet op een niet-admin-account.

Als het toch Task Scheduler wordt, dan minimaal deze XML:

```xml
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers><LogonTrigger><UserId>%USERDOMAIN%\%USERNAME%</UserId><Delay>PT30S</Delay></LogonTrigger></Triggers>
  <Principals><Principal id="u"><UserId>%USERDOMAIN%\%USERNAME%</UserId>
    <LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>5</Priority>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <RestartOnFailure><Interval>PT1M</Interval><Count>3</Count></RestartOnFailure>
  </Settings>
  <Actions Context="u"><Exec><Command>%LOCALAPPDATA%\Programs\MyScribe\MyScribe.exe</Command>
    <Arguments>--headless --at-login --no-browser</Arguments></Exec></Actions>
</Task>
```

De `%...%`-waarden moeten bij het registreren ingevuld worden. Ze zijn hier alleen illustratief.

**Aanbevolen configuratie voor Windows:** houd de Run-waarde en voeg `--headless` toe.

```
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
  MyScribe = "C:\Users\<u>\AppData\Local\Programs\MyScribe\MyScribe.exe" --headless --at-login --no-browser
```

Waarom dit wint van Task Scheduler:
- Het is al gebouwd en getest (`autostart.py`, 22 tests).
- Het heeft geen accu-, tijdslimiet- of prioriteitsvallen, en geen admin-onzekerheid.
- De gebruiker ziet het item in Taakbeheer onder Opstarten (bekend gedrag, in deze ronde niet met een primaire bron nagelopen).
- Herstart na een crash ontbreekt. Een crash van uvicorn is zeldzaam, want de zware GPU-code draait in runner-children.

**Installer en uninstaller:**
1. `[UninstallRun]`: stop de server eerst. Gebruik de nieuwe stopdeur (zie §3) met `taskkill /im MyScribe.exe /t /f` als fallback, en wacht een paar seconden. Ollama doet precies dat (taskkill plus `timeout 5`).
2. Update: geef `PrepareToInstall` in `[Code]` dezelfde stop. Zonder stop blijft de oude server de oude code draaien. De post-install `[Run]` ziet `/health` antwoorden en opent alleen de browser (`prepare`, `:1544-1550`), waardoor de re-sync tot de volgende login wacht. Restart Manager (`CloseApplications`) kijkt alleen naar bestanden die `[Files]` vervangt. Het ziet dus wel `MyScribe.exe`, maar niet `python.exe` in `%LOCALAPPDATA%\MyScribe`. Hoe Restart Manager met een vensterloos proces omgaat, is niet geverifieerd: niet op leunen.
3. Start na een update opnieuw met `--headless --at-login --no-browser` als het login-item aan staat.
4. De Run-waarde verwijderen staat al goed (iss:53).

### 2.2 macOS

| Optie | Vereist | Toezicht en logs | Oordeel |
|---|---|---|---|
| **LaunchAgent in `~/Library/LaunchAgents`** (bestaat) | niets | launchd: `KeepAlive`, `StandardOutPath`, `ExitTimeOut` | **Aanbevolen nu**, mits de plist wordt aangepast |
| `SMAppService.agent(plistName:)` (macOS 13+) | plist in `Contents/Library/LaunchAgents`. Ondertekening vrijwel zeker nodig; ad-hoc niet geverifieerd. | idem, en een nette plek in Login Items | **Doel zodra er een Developer ID is.** Ollama doet dit, met fallback naar `~/Library/LaunchAgents`. |
| Login Item (`SMAppService.mainApp`) | ondertekening | geen toezicht | geen winst |
| LaunchDaemon | admin, draait als root, geen GUI-sessie | — | afgewezen |

Problemen in de huidige plist (`autostart.py:169-179, 317`):
- **`open -a` keert direct terug.** launchd houdt dan niets in de gaten, `StandardOutPath` vangt niets op, en `KeepAlive` zou een respawn-lus geven.
- **Het venster verschijnt toch,** want er staat geen `--headless` in.
- **`AssociatedBundleIdentifiers` ontbreekt.** Volgens de launchd.plist-man page koppelt die sleutel een losse plist aan de app in Login Items.
- **App Translocation.** Een ongetekende app met quarantaine-vlag die vanuit Downloads of de dmg wordt geopend, draait vanaf een willekeurig read-only pad (Eclectic Light, secundair; Apple documenteert het exacte gedrag niet). Dan registreert `MYSCRIBE_LAUNCHER` een pad dat bij de volgende login weg is. Weiger te registreren als het pad `AppTranslocation` bevat.
- **TCC-toestemming.** Een bibliotheek of watch-map in `~/Documents` of `~/Downloads` kan bij login een toestemmingsvraag geven. Niet geverifieerd.

**Aanbevolen plist:**

```xml
<dict>
  <key>Label</key><string>io.github.rvdbreemen.myscribe</string>
  <key>ProgramArguments</key><array>
    <string>/Applications/MyScribe.app/Contents/MacOS/MyScribe</string>
    <string>--headless</string><string>--at-login</string><string>--no-browser</string></array>
  <key>AssociatedBundleIdentifiers</key><array><string>io.github.rvdbreemen.myscribe</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <key>ProcessType</key><string>Interactive</string>
  <key>LimitLoadToSessionType</key><string>Aqua</string>
  <key>ExitTimeOut</key><integer>40</integer>
  <key>StandardOutPath</key><string>/Users/u/Library/Logs/MyScribe/launchd.log</string>
  <key>StandardErrorPath</key><string>/Users/u/Library/Logs/MyScribe/launchd.log</string>
</dict>
```

Toelichting per sleutel:
- `ProcessType Interactive`: `Background` krijgt volgens de man page resourcelimieten.
- `KeepAlive/SuccessfulExit=false`: herstart alleen na een niet-nul exit. Dat werkt pas als `run_headless` bij een onverwachte dood niet-nul teruggeeft (§1).
- `ExitTimeOut 40`: de launcher wacht tot 2×15 s.
- Het pad naar de binary staat in de plist en moet bij elke start worden gecontroleerd en zo nodig herschreven: de app kan verplaatst worden.
- Ollama's `LSUIElement` hoort in Info.plist, niet in een launchd-plist. Niet overnemen.

**Stoppen:** de stopdeur geeft exit 0, dus geen herstart. Daarnaast `launchctl bootout gui/$(id -u)/io.github.rvdbreemen.myscribe`. Zonder `launchctl bootstrap` wordt een nieuwe plist pas bij de volgende login geladen. De Settings-switch zou `launchctl bootstrap gui/$UID <plist>` moeten aanroepen.

**Uninstall:** er is geen uninstaller.
- Een controle bij de start dekt alleen een *verplaatste* app. Een verwijderde app start niets en ruimt dus ook niets op.
- Daarom blijft het bij de docs: zet eerst de Settings-switch uit, of verwijder de plist met de hand. `docs/installation.md:198-207` moet daarop worden aangepast, voor macOS en voor Linux.
- Restrisico: een verweesde plist die bij elke login faalt.
- De Settings-switch moet `~/Library/Logs/MyScribe` aanmaken vóór hij de plist schrijft. De man page zegt alleen dat launchd het *bestand* aanmaakt, niets over de map.

### 2.3 Linux (AppImage)

| Optie | Toezicht | Logs | Oordeel |
|---|---|---|---|
| **systemd user unit** | `Restart=on-failure`, cgroup-kill | journald | **Aanbevolen** |
| XDG autostart `.desktop` (bestaat) | geen. systemd-xdg-autostart-generator maakt er wel units van, maar zonder herstartgarantie in de docs. | geen | fallback zonder systemd user session |
| systeemunit (`/etc/systemd/system`, zoals Ollama) | ja | journald | afgewezen: root, en een ander profiel |
| `loginctl enable-linger` | user manager vanaf boot, ook na logout | — | opt-in. Op een laptop zelden gewenst (Syncthing: user service voor desktops). |

**Aanbevolen unit** (`~/.config/systemd/user/myscribe.service`), naar het model van Syncthing's eigen user unit:

```ini
[Unit]
Description=MyScribe - local transcription server
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Type=simple
ExecStart=/home/u/Applications/MyScribe-x86_64.AppImage --headless --at-login --no-browser
Restart=on-failure
RestartSec=10
# alleen bij XDG_DATA_HOME in het profiel: Environment=XDG_DATA_HOME=/pad
KillMode=mixed
TimeoutStopSec=45

[Install]
WantedBy=default.target
```

De Settings-switch schrijft dit bestand en draait `systemctl --user daemon-reload && systemctl --user enable --now myscribe`. Uit is `disable --now` en daarna het bestand verwijderen. Logs: `journalctl --user -u myscribe`.

Waarom deze sleutels:
- `--headless` is hier essentieel: een user unit heeft geen display, en `tkinter_present()` zegt toch ja.
- `KillMode=mixed`: SIGTERM gaat naar de launcher, die zijn procesgroep netjes stopt. Restanten krijgen SIGKILL.

**De omgeving van de user manager.** De systemd user manager krijgt de omgeving uit `.profile` of `.bashrc` niet mee.
- `default_home()` en `pointer_path()` lezen `XDG_DATA_HOME` (launcher `:66-100`).
- Is die variabele alleen in de shell gezet, dan opent de achtergrondserver stil een andere bibliotheek dan een handstart.
- Oplossing: schrijf bij registratie de opgeloste waarde als `Environment=` in de unit, en alleen als hij gezet is.
- Niet `MYSCRIBE_HOME` gebruiken: die slaat de geadopteerde bibliotheek over (ADR-019, launcher `:2971`).
- macOS en Windows hebben dit probleem niet: daar komt de home uit `Path.home()` en `LOCALAPPDATA`.

**Uninstall:**
- Settings-switch uit, of met de hand `systemctl --user disable --now myscribe` en daarna de unit verwijderen.
- Een verwijderde AppImage zonder deze stap geeft `203/EXEC`. systemd probeert het dan 5 keer binnen `StartLimitIntervalSec` en zet de unit op failed. Daarna blijft de verweesde unit staan.

**AppImage-valkuilen:**
- `$APPIMAGE` is het pad met symlinks opgelost (docs.appimage.org). Een symlink naar een geversioneerd bestand registreert dus de oude versie.
- Een verplaatste of hernoemde AppImage breekt de unit. Controleer en herschrijf bij elke start.
- Zonder libfuse2 start een AppImage niet. `APPIMAGE_EXTRACT_AND_RUN=1` is de uitwijk, maar die pakt elke start uit.

**NVIDIA na suspend:** zonder `NVreg_PreserveVideoMemoryAllocations` en de `nvidia-suspend/resume`-units kan CUDA na resume falen (forumbronnen, secundair; de NVIDIA-README zelf kon ik niet ophalen: 404). Dat treft alleen een job die door de slaap heen loopt. Het webproces heeft geen GPU-context.

---

## 3. Platformoverstijgend

1. **Eén servermodus.** `--headless --at-login --no-browser` is dat al. Eventueel kan `--background` als alias dienen, zodat de items leesbaar blijven. Zonder stdout moet elke fout in `launcher.log` belanden. De vroege `console()`-regels in `main` (vóór er een Layout is, `:2947-2970`) printen nu nergens heen. Een niet-aangesloten bibliotheekschijf bij login eindigt zo stil.
2. **Exitcodes in klassen.** Vandaag geeft de launcher al 1 terug bij configuratiefouten:
   - geen home, bijvoorbeeld een bibliotheekschijf die niet is aangesloten (`main`, `:2962-2970`);
   - `first_run` mislukt (`:2208`): poort bezet, of `uv sync` offline na een update.

   Met `KeepAlive/SuccessfulExit=false` of `Restart=on-failure` wordt dat een herstartlus. launchd herstart dan elke ~10 s zonder plafond, en een mislukte sync van meerdere GB herhaalt zich op accu. De afspraak wordt daarom:

   | Exitcode | Betekenis | Gevolg |
   |---|---|---|
   | 0 | nette stop, een andere instantie serveert al, of een configuratieprobleem | geen herstart; het probleem wordt gelogd |
   | eigen code, bv. 70 | echte crash van het app-child | herstart |

   launchd kent alleen nul versus niet-nul. systemd kan het fijner met `RestartPreventExitStatus=`.
3. **Stopdeur.** Twee onderdelen:
   - `POST /api/shutdown`: alleen loopback. Zet `server.should_exit`, zodat de lifespan supervisor, watcher en feeds netjes stopt.
     - Een cross-site POST vanuit een webpagina weigert `SameOriginPosts` al (`scribe/guard.py:23-25, 57-69`, op `Sec-Fetch-Site` en `Origin`).
     - Een lokaal proces komt er wel door, maar dat kan nu ook al alles.
     - Een tokenbestand in de home dat `--stop` leest, is de strengere variant: keuze voor de ADR.
   - `MyScribe --stop`: roept de route aan, met hard kill als fallback.

   Installer, uninstaller, tray en een "Stop"-knop in de web-UI gebruiken alle vier deze deur. Wat er met een lopende job gebeurt (wachten, annuleren of interrupted), is een ontwerpkeuze.
4. **Health en ready.** `/health` bestaat en antwoordt pas na de lifespan. Voeg `running_jobs` toe, zodat installer en tray kunnen waarschuwen voordat ze stoppen.
5. **Single instance.** Zet een exclusieve lock op een bestand in de home (`msvcrt.locking` of `fcntl.flock`, stdlib) vóór de `/health`-probe. Dat sluit het race-venster tussen login-item en een handstart.
6. **Poort bezet.** Nu verschijnt alleen een foutregel (`:1552`). In de achtergrond ziet niemand die. Log hem en laat hem zien bij de volgende handstart. Een tray kan hem tonen.
7. **De UI vinden.** Bij een draaiende server opent de bestaande snelkoppeling/app al alleen de browser (`prepare`). Het Start-menu-item wordt zo "Open MyScribe". Geen extra werk nodig.
8. **Slaap en resume.**
   - De server zelf overleeft slaap.
   - Feeds halen achterstand in.
   - Een runner die door de slaap heen loopt, kan falen. Overweeg tijdens een job een slaap-inhibitor: `SetThreadExecutionState(ES_SYSTEM_REQUIRED)`, `caffeinate -i -w <pid>` of `systemd-inhibit --what=sleep`. Dichtklappen op macOS forceert slaap toch.
9. **Afmelden en afsluiten.** Windows beëindigt processen bij logoff. Uvicorn stopt dan vermoedelijk niet netjes (afleiding, niet gemeten), en reconcile vangt de wees op.
10. **Updates.** Stop, vervang, start. Zie de installerpunten in §2.1. Op macOS en Linux vervangt de gebruiker het bundle of de AppImage zelf. Pas de volgende start synct.
   - Tijdens `PrepareToInstall` staat nog de *oude* `MyScribe.exe` geïnstalleerd. Bij de eerste update met `--stop` kent die de vlag nog niet. De `[Code]` van de installer roept daarom zelf de HTTP-route aan, met taskkill als fallback.
11. **Migratie.** Bestaande Run-waarden, plists en `.desktop`-bestanden bevatten het oude commando, zonder `--headless`. Herschrijf ze bij de start als ze afwijken van `start_command()`, op alle drie de platforms.
12. **Tray-icoon (optionele laag).**
    - Waarom zou je het willen: een tray maakt "draait hij?" en "Stop" zichtbaar. Ollama is het referentievoorbeeld: een tray-app via de Startup-`.lnk` op Windows en een SMAppService-agent op macOS.
    - Kanttekeningen bij pystray 0.19.5: laatste release 2023-09-17, LGPL-3.0, lage activiteit. Op GNOME heeft het een AppIndicator-extensie nodig. In de launcher breekt het ADR-011's stdlib-only, tenzij het alleen in de frozen build zit.
    - Advies: eerst geen tray, wel een "Stop MyScribe"-knop in de web-UI. Een tray komt later, met een eigen ADR.

---

## 4. Beslissingen die een ADR vragen

1. **Achtergrondmodus = login-item per gebruiker, geen systeemservice.** Per OS het mechanisme (Run-waarde, LaunchAgent naar SMAppService, systemd user unit met XDG als fallback) en het startcommando met `--headless`. Dit verandert wat TASK-089.21 openliet ("the mechanism per OS is NOT decided here").
2. **Het stopcontract.** `POST /api/shutdown` plus `--stop`: wie mag het aanroepen, en wat er met een lopende job gebeurt.
3. **Tray ja of nee, en waar die woont.** Raakt ADR-011 (stdlib-only).
4. **Ondertekening op macOS en SMAppService.** Hangt af van een Developer ID. ADR-011 noemt dat nu als kostenpost.
5. **Herstart na een crash ja of nee.** Dat bepaalt Run-waarde versus Task Scheduler op Windows. Optioneel: een slaap-inhibitor tijdens jobs.

---

## 5. Wat nog geverifieerd moet worden (door Robert)

1. **Windows, onzichtbare start.** Zet `--headless` handmatig in de Run-waarde, meld af en weer aan. Verwacht:
   - geen venster;
   - `curl -s http://127.0.0.1:4242/health` geeft `{"ok":true,...}`;
   - in Taakbeheer staan `MyScribe.exe` en `python.exe`, zonder console.

   Ik heb dit alleen uit de code afgeleid, niet gedraaid.
2. **Task Scheduler-XML-import door een niet-admin-account.** Alleen nodig als besluit 5 "ja" wordt.
3. **macOS-plist met directe binary en `--headless`,** op de Mac van de eigenaar (punt 6 van `docs/macos-acceptance.md`, aangepast).
4. **Linux-unit:** heeft een echte desktop-login nodig. WSL telt niet.

---

## 6. Bronnen

Primair:
- MS Learn, Run- en RunOnce-sleutels: https://learn.microsoft.com/en-us/windows/win32/setupapi/run-and-runonce-registry-keys
- MS Learn, Interactive Services (sessie 0): https://learn.microsoft.com/en-us/windows/win32/services/interactive-services
- MS Learn, DisallowStartIfOnBatteries: https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-disallowstartifonbatteries
- MS Learn, ExecutionTimeLimit: https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-executiontimelimit
- MS Learn, StopIfGoingOnBatteries: https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-stopifgoingonbatteries-settingstype-element
- MS Learn, Priority: https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-priority-settingstype-element
- MS Learn, RestartOnFailure: https://learn.microsoft.com/en-us/windows/win32/taskschd/taskschedulerschema-restartonfailure-settingstype-element
- MS Learn, Scheduling Priorities (overerving van de prioriteitsklasse): https://learn.microsoft.com/en-us/windows/win32/procthread/scheduling-priorities
- Inno Setup, CloseApplications: https://jrsoftware.org/ishelp/topic_setup_closeapplications.htm
- Apple, SMAppService: https://developer.apple.com/documentation/servicemanagement/smappservice
- Apple, agent(plistName:): https://developer.apple.com/documentation/servicemanagement/smappservice/agent(plistname:)
- launchd.plist(5): https://keith.github.io/xcode-man-pages/launchd.plist.5.html
- Apple, beheer van login items en achtergrondtaken: https://support.apple.com/guide/deployment/manage-login-items-background-tasks-mac-depdca572563/web
- systemd, loginctl: https://www.freedesktop.org/software/systemd/man/latest/loginctl.html
- systemd.kill: https://www.freedesktop.org/software/systemd/man/latest/systemd.kill.html
- systemd-xdg-autostart-generator: https://www.freedesktop.org/software/systemd/man/latest/systemd-xdg-autostart-generator.html
- AppImage, omgevingsvariabelen: https://docs.appimage.org/packaging-guide/environment-variables.html

Referentie-implementaties (code gelezen via `gh api`):
- Ollama, Windows-installer: `app/ollama.iss`
- Ollama, Startup-`.lnk`: `app/cmd/app/app_windows.go`
- Ollama, LaunchAgent-plist: `app/darwin/Ollama.app/Contents/Library/LaunchAgents/com.ollama.ollama.plist`
- Ollama, SMAppService: `app/cmd/app/app_darwin.m`
- Ollama-docs: https://docs.ollama.com/windows en https://docs.ollama.com/linux
- Syncthing: https://docs.syncthing.net/users/autostart.html, met `etc/linux-systemd/user/syncthing.service` en `etc/macos-launchd/syncthing.plist`

Versies (opgehaald op 2026-10-19):
- WinSW: https://github.com/winsw/winsw (v2.12.0 stabiel, v3.0.0-alpha.11)
- NSSM: https://nssm.cc/download (2.24 uit 2014, pre-release uit 2017)
- Servy: https://github.com/aelassas/servy (v10.5, 2026-10-15)
- pystray: https://pypi.org/project/pystray/ (0.19.5, 2023-09-17)

Secundair (alleen als ondersteuning):
- NVIDIA-forum over CUDA in services: https://forums.developer.nvidia.com/t/cuda-from-a-windows-service/35546
- habr-Q&A over `schtasks onlogon`: https://qna.habr.com/q/1303758
- Eclectic Light over App Translocation: https://eclecticlight.co/2024/05/14/lost-in-translocation/
- Arch- en NVIDIA-forum over suspend: https://bbs.archlinux.org/viewtopic.php?id=314302
