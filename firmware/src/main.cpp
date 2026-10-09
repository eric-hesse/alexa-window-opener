// Fensteroeffner - Grundprogramm (noch ohne Motor)
//
// 1) WLAN einrichten OHNE Programmieren:
//    Findet der ESP32 kein bekanntes WLAN, oeffnet er ein eigenes WLAN namens
//    "Fensteroeffner-Setup". Mit Handy/iPad verbinden -> Seite oeffnet sich
//    (sonst im Browser 192.168.4.1) -> "Configure WiFi" -> Heim-WLAN + Passwort -> Save.
//    WLAN vergessen: BOOT-Taste beim Einstecken/Reset 3 Sekunden gedrueckt halten.
//
// 2) Alexa: Geraet heisst "Fenster".
//    "Alexa, schalte Fenster ein" / "... aus" / "Alexa, stelle Fenster auf 50 Prozent"
//
// 3) Update OHNE Kabel (z. B. vom iPad):
//    Im selben WLAN im Browser  http://fenster.local/update  oeffnen
//    (oder http://<IP-Adresse>/update), Datei firmware.bin waehlen, hochladen.
//    firmware.bin entsteht in VS Code mit dem Haken (Build) unter
//    .pio/build/esp32dev/firmware.bin

#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include <Update.h>
#include <WiFiManager.h>
#include <Espalexa.h>

const char* VERSION = "0.2 (Alexa-Test + Web-Update)";
const int LED_PIN  = 2;    // bei vielen ESP32-Boards eine kleine LED, sonst egal
const int BOOT_PIN = 0;    // BOOT-Taste auf dem Board

WebServer server(80);
Espalexa espalexa;
int letzterWert = 0;

void fensterGeaendert(uint8_t helligkeit) {
  letzterWert = (helligkeit * 100 + 127) / 255;
  Serial.printf("Alexa-Befehl: Fenster auf %d %%\n", letzterWert);
  digitalWrite(LED_PIN, letzterWert > 0 ? HIGH : LOW);
  // Spaeter: hier faehrt der Motor das Fenster auf 'letzterWert'.
}

// ---------- Webseiten ----------
const char* SEITE_KOPF =
  "<!doctype html><html><head><meta charset='utf-8'>"
  "<meta name='viewport' content='width=device-width,initial-scale=1'>"
  "<title>Fensteroeffner</title><style>"
  "body{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:480px;margin:24px auto;padding:0 16px;color:#222}"
  "h1{font-size:1.4em}.box{border:1px solid #ccc;border-radius:10px;padding:16px;margin:16px 0}"
  "button,input[type=submit]{font-size:1em;padding:10px 18px;border-radius:8px;border:0;background:#2a6edb;color:#fff}"
  "</style></head><body>";

void seiteStart() {
  String s = SEITE_KOPF;
  s += "<h1>Fensteroeffner</h1>";
  s += "<div class='box'>Version: " + String(VERSION) + "<br>WLAN: " + WiFi.SSID() +
       "<br>IP: " + WiFi.localIP().toString() + "<br>Letzter Befehl: " + String(letzterWert) + " %</div>";
  s += "<div class='box'><a href='/update'>Programm aktualisieren</a></div></body></html>";
  server.send(200, "text/html", s);
}

void seiteUpdate() {
  String s = SEITE_KOPF;
  s += "<h1>Programm aktualisieren</h1><div class='box'>"
       "Datei <b>firmware.bin</b> auswaehlen und hochladen. Danach startet der ESP32 neu.<br><br>"
       "<form method='POST' action='/update' enctype='multipart/form-data'>"
       "<input type='file' name='firmware' accept='.bin'><br><br>"
       "<input type='submit' value='Hochladen'></form></div></body></html>";
  server.send(200, "text/html", s);
}

void updateFertig() {
  bool ok = !Update.hasError();
  String s = SEITE_KOPF;
  s += ok ? "<h1>Update erfolgreich</h1><p>Der ESP32 startet neu. Seite in 10 Sekunden neu laden.</p>"
          : "<h1>Update fehlgeschlagen</h1><p>Bitte nochmal versuchen (richtige Datei firmware.bin?).</p>";
  s += "</body></html>";
  server.sendHeader("Connection", "close");
  server.send(200, "text/html", s);
  delay(500);
  if (ok) ESP.restart();
}

void updateEmpfangen() {
  HTTPUpload& up = server.upload();
  if (up.status == UPLOAD_FILE_START) {
    Serial.printf("Update startet: %s\n", up.filename.c_str());
    if (!Update.begin(UPDATE_SIZE_UNKNOWN)) Update.printError(Serial);
  } else if (up.status == UPLOAD_FILE_WRITE) {
    if (Update.write(up.buf, up.currentSize) != up.currentSize) Update.printError(Serial);
  } else if (up.status == UPLOAD_FILE_END) {
    if (Update.end(true)) Serial.printf("Update fertig: %u Bytes\n", up.totalSize);
    else Update.printError(Serial);
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.printf("\nFensteroeffner Version %s\n", VERSION);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BOOT_PIN, INPUT_PULLUP);

  WiFiManager wm;
  if (digitalRead(BOOT_PIN) == LOW) {
    Serial.println("BOOT-Taste gedrueckt: halte 3 Sekunden zum Loeschen der WLAN-Daten ...");
    delay(3000);
    if (digitalRead(BOOT_PIN) == LOW) {
      wm.resetSettings();
      Serial.println("WLAN-Daten geloescht.");
    }
  }

  Serial.println("Verbinde mit gespeichertem WLAN ...");
  Serial.println("(Falls keins bekannt: ins WLAN \"Fensteroeffner-Setup\" gehen)");
  wm.setConfigPortalTimeout(300);
  if (!wm.autoConnect("Fensteroeffner-Setup")) {
    Serial.println("Kein WLAN eingerichtet. Starte neu ...");
    delay(1000);
    ESP.restart();
  }
  Serial.print("Verbunden mit \"");
  Serial.print(WiFi.SSID());
  Serial.print("\", IP-Adresse: ");
  Serial.println(WiFi.localIP());

  if (MDNS.begin("fenster")) Serial.println("Erreichbar unter http://fenster.local");

  // Eigene Seiten + Alexa teilen sich denselben Webserver
  server.on("/", HTTP_GET, seiteStart);
  server.on("/update", HTTP_GET, seiteUpdate);
  server.on("/update", HTTP_POST, updateFertig, updateEmpfangen);
  server.onNotFound([]() {
    if (!espalexa.handleAlexaApiCall(server.uri(), server.arg(0))) {
      server.send(404, "text/plain", "Nicht gefunden");
    }
  });

  espalexa.addDevice("Fenster", fensterGeaendert);
  espalexa.begin(&server);
  MDNS.addService("http", "tcp", 80);
  Serial.println("Bereit. Alexa-App: Geraete -> + -> Geraet hinzufuegen -> Sonstiges -> Geraete suchen.");
}

void loop() {
  espalexa.loop();   // bedient auch den Webserver
  delay(1);
}
