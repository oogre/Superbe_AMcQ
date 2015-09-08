/*
  NUM_READINGS ---- DEFAULT 10
  MATH AN AVERAGE ON "NUM_READINGS" VALUES TO DEFINE STATE
*/
#define NUM_READINGS        5

/*
  NUM_TO_BE_SURE ---- DEFAULT 10
  STATE HAVE TO BE THE SAME DURING "NUM_TO_BE_SURE" MESURMENTS TO BE VALIDATED
*/
#define NUM_TO_BE_SURE      3


// VAR FOR DECISION : areYouSure()
int sure_cmp = 0;
boolean flying_state = false;

// VAR FOR AVERAGING : getSensorValue()
int readings [NUM_READINGS];
int index = 0;
long total = 0;
boolean ready = false;

void initFlyingSensor () {
  for (int i = 0 ; i < NUM_READINGS ; i ++)
  {
    readings[i] = 0;
  }
}

int getSensorValue()
{
  total = total - readings[index];
  readings[index] = pulseIn(USechoPin, HIGH) / 58;
  total = total + readings[index];
  index ++;
  if (index >= NUM_READINGS)
  {
    index = 0;
    ready = true;
  }
  int tmp = total / NUM_READINGS;
  Serial.print(tmp);
  return tmp;
}

bool isRockFlying (int value)
{
  return value < analogRead(seuilPin) && value >= 75;
}

byte areYouSure(bool isFlying)
{
  if (flying_state == isFlying)
  {
    sure_cmp ++;
    if (sure_cmp >= NUM_TO_BE_SURE)
    {
      return isFlying ? 1 : 0;
    }
  }
  else
  {
    flying_state = isFlying;
    sure_cmp = 0;
  }
  return 2;
}
