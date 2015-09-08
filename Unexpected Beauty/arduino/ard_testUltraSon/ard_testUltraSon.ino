
//constante a changer :
const int dureeChangement = 200;
const int valVeille1 = 0;
const int valActif1 = 255;
const int valVeille2 = 255;
const int valActif2 = 0;
const int dureeDelayLoop = 20;
const int mesureCycle = 5;  //max 20fps pour le capteur US
const boolean serialEnable = true;  //console Serie active ou pas

#include <DmxSimple.h>

const int ledAPin = 10;
const int ledBPin = 11;
const int dmxPin = 9;
const int pushPin = 12;
const int UStrigPin = 8;
const int USechoPin = 7;
const int seuilPin = A3;
int compteur = 0;
boolean actif = false;
int compteurMesureCycle = 0;

void setup() {
  initFlyingSensor();
  pinMode(ledAPin, OUTPUT);
  pinMode(ledBPin, OUTPUT);
  pinMode(pushPin, INPUT);
  pinMode(UStrigPin, OUTPUT);
  pinMode(USechoPin, INPUT);
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
  compteurMesureCycle ++;
  if (compteurMesureCycle >= mesureCycle) {
    compteurMesureCycle = 0;
    digitalWrite(UStrigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(UStrigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(UStrigPin, LOW);
    /*int distance = pulseIn(USechoPin, HIGH) / 58;
    if (distance < analogRead(seuilPin)) {
      actif = true;
      digitalWrite(ledAPin, HIGH);
      digitalWrite(ledBPin, LOW);
    } else {
      actif = false;
      digitalWrite(ledAPin, LOW);
      digitalWrite(ledBPin, HIGH);
    }
    */
    switch (areYouSure(isRockFlying(getSensorValue()))) {
      case 1 :  // ROCK IS FELL
        actif = true;
        digitalWrite(ledAPin, HIGH);
        digitalWrite(ledBPin, LOW);
        break;
      case 0:   // ROCK IS FLYIN
        actif = false;
        digitalWrite(ledAPin, LOW);
        digitalWrite(ledBPin, HIGH);
        break;
      case 2 :  // ROCK STATE NOT SURE
        // NOTHING
        break;
    }
    //----- retour serie eventuel -----
    if (serialEnable) {
      Serial.print(" ");
      Serial.print(analogRead(seuilPin));
      Serial.print(" ");
      Serial.println(actif);
      
    }
    //----- bouton inversion effet -----
    if (digitalRead(pushPin) == LOW) {
      actif = !actif;
    }
  }

  //----- avance des compteurs -----
  if (actif) {
    if (compteur < dureeChangement) compteur++;
  } else {
    if (compteur > 0) compteur--;
  }

  //----- DMX -----
  DmxSimple.write(7, map(compteur, 0, dureeChangement, valVeille1, valActif1));
  DmxSimple.write(6, map(compteur, 0, dureeChangement, valVeille2, valActif2));

  delay(dureeDelayLoop);
}
