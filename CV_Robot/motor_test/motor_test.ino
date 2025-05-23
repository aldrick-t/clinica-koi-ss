// H-Bridge Pins (Customize these to your available GPIOs)
#define ENA 5     // PWM for Motor A speed (must be PWM-capable)
#define IN1 18    // Motor A direction
#define IN2 19    // Motor A direction
#define IN3 21    // Motor B direction (changed from 16)
#define IN4 22    // Motor B direction (changed from 4)
#define ENB 23    // PWM for Motor B speed (must be PWM-capable)

void setup() {
  Serial.begin(115200);
  
  // Set motor control pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  Serial.println("Motor Test Started");
}

void loop() {
  // Test Motor A Forward (IN1=HIGH, IN2=LOW)
  Serial.println("Motor A Forward");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(ENA, 255);  // ~78% speed
  delay(2000);

  // Stop
  Serial.println("Stop");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
  delay(1000);

  // Test Motor A Reverse (IN1=LOW, IN2=HIGH)
  Serial.println("Motor A Reverse");
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 255);
  delay(2000);

  // Stop
  Serial.println("Stop");
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  analogWrite(ENA, 0);
  delay(1000);

  // Test Motor B Forward (IN3=HIGH, IN4=LOW)
  Serial.println("Motor B Forward");
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 255);
  delay(2000);

  // Stop
  Serial.println("Stop");
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
  delay(1000);

  // Test Motor B Reverse (IN3=LOW, IN4=HIGH)
  Serial.println("Motor B Reverse");
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENB, 255);
  delay(2000);

  // Stop
  Serial.println("Stop");
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENB, 0);
  delay(1000);
}