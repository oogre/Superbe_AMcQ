
//constante a changer :
const int dureeChangement = 200;
const int valVeille1 = -100;
const int valActif1 = 255;
const int valVeille2 = 255;
const int valActif2 = -20;
const int dureeDelayLoop = 20;
const boolean serialEnable = true;  //console Serie active ou pas

#include <DmxSimple.h>

const int ledAPin = 10;
const int ledBPin = 11;
const int dmxPin = 9;
const int pushPin = 12;
const int IRPin = A0;
const int seuilPin = A3;
int compteur = 0;
boolean actif = false;

void setup() {
  pinMode(ledAPin, OUTPUT);
  pinMode(ledBPin, OUTPUT);
  pinMode(pushPin, INPUT);
  DmxSimple.usePin(dmxPin);
  DmxSimple.maxChannel(7);
  DmxSimple.write(1, 127);  //declaration des canaux DMX qui ne changent pas
  DmxSimple.write(2, 127);
  DmxSimple.write(3, 255);
  DmxSimple.write(4, 0);
  DmxSimple.write(5, 0);
  DmxSimple.write(6, 0);
  DmxSimple.write(7, 0);
  Serial.begin(9600);
}

void loop() {
  //----- mesure distance et du seuil -----
  if (analogRead(IRPin) > analogRead(seuilPin)) {
    actif = true;
    digitalWrite(ledAPin, HIGH);
    digitalWrite(ledBPin, LOW);
  } else {
    actif = false;
    digitalWrite(ledAPin, LOW);
    digitalWrite(ledBPin, HIGH);
  }
//----- retour serie eventuel -----
  if (serialEnable) {
    Serial.print(analogRead(IRPin));
    Serial.print(" ");
    Serial.println(analogRead(seuilPin));
  }
//----- bouton inversion effet -----
  if (digitalRead(pushPin) == LOW) {
    actif = !actif;
  }

  //----- avance des compteurs -----
  if (actif) {
    if (compteur < dureeChangement) compteur++;
  } else {
    if (compteur > 0) compteur--;
  } 

  //----- DMX -----
  int valeurDMX = map(compteur, 0, dureeChangement, valVeille1, valActif1);
  valeurDMX = constrain(valeurDMX, 0, 255);
  DmxSimple.write(4, valeurDMX);
  valeurDMX = map(compteur, 0, dureeChangement, valVeille2, valActif2);
  valeurDMX = constrain(valeurDMX, 0, 255);
  DmxSimple.write(6, valeurDMX);

  delay(dureeDelayLoop);
}
