//sortie en 3V3 pour RPI

//constante a changer :
const int dureeChangement = 100;
const int valVeille1 = 0;
const int valActif1 = 255;
const int valActif2 = 0;  //le seuilVeille2 est la respiration
const int dureeRespiration = 200;
const int valBasRespiration = 180;
const int valHautRespiration = 200;
const int dureeDelayLoop = 20;
const boolean serialEnable = true;  //console Serie active ou pas

#include <DmxSimple.h>

const int ledAPin = 3;
const int ledBPin = 4;
const int lightAPin = 5;
const int lightBPin = 6;
const int dmxPin = 7;
const int balanceAPin = A0;
const int balanceBPin = A1;
const int seuilAPin = A2;
const int seuilBPin = A3;
int compteur = 0;
int compteurRespiration = 0;

void setup() {
  pinMode(ledAPin, OUTPUT);
  pinMode(ledBPin, OUTPUT);
  pinMode(lightAPin, OUTPUT);
  pinMode(lightBPin, OUTPUT);
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
  //----- mesure des balances et des seuils -----
  boolean actif = false;
  if (analogRead(balanceAPin) < analogRead(seuilAPin)) {
    digitalWrite(ledAPin, HIGH);
    actif = true;
  } else {
    digitalWrite(ledAPin, LOW);
  }
  if (analogRead(balanceBPin) < analogRead(seuilBPin)) {
    digitalWrite(ledBPin, HIGH);
    actif = true;
  } else {
    digitalWrite(ledBPin, LOW);
  }

  //----- avance des compteurs et calcul de la respiration -----
  if (actif) {
    if (compteur < dureeChangement) compteur++;
  } else {
    if (compteur > 0) compteur--;
  }
  int respiration = valHautRespiration;
  if (compteurRespiration < dureeRespiration/2) {
    respiration = map(compteurRespiration, 0, dureeRespiration/2, valHautRespiration, valBasRespiration);    
    compteurRespiration++;
  } else if (compteurRespiration < dureeRespiration) {
    respiration = map(compteurRespiration, dureeRespiration/2, dureeRespiration, valBasRespiration, valHautRespiration);    
    compteurRespiration++;
  } else compteurRespiration = 0;  

  //----- PWM et DMX -----
  analogWrite(lightAPin, map(compteur, 0, dureeChangement, valVeille1, valActif1));
  analogWrite(lightBPin, map(compteur, 0, dureeChangement, respiration, valActif2));
  DmxSimple.write(4, map(compteur, 0, dureeChangement, valVeille1, valActif1));
  DmxSimple.write(5, map(compteur, 0, dureeChangement, respiration, valActif2));

  //----- retour serie eventuel -----
  if (serialEnable) {
    Serial.print(analogRead(balanceAPin));
    Serial.print(" ");
    Serial.print(analogRead(balanceBPin));
    Serial.print(" ");
    Serial.print(analogRead(seuilAPin));
    Serial.print(" ");
    Serial.println(analogRead(seuilBPin));
  }
  delay(dureeDelayLoop);
}
