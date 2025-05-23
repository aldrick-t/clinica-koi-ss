#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "EJVG Galaxy A34 5G";
const char* password = "s1rius25";
const char* mqtt_server = "192.168.233.174";  // IP del broker
WiFiClient espClient;
PubSubClient client(espClient);

// Pines del H-Bridge (ajusta si es necesario)
#define ENA 5     // PWM for Motor A speed (must be PWM-capable)
#define IN1 18    // Motor A direction
#define IN2 19    // Motor A direction
#define IN3 21    // Motor B direction (changed from 16)
#define IN4 22    // Motor B direction (changed from 4)
#define ENB 23    // PWM for Motor B speed (must be PWM-capable)


#define LIGHT_PIN 2

void setup_wifi() {
  delay(10);
  Serial.println("Conectando a WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String command = "";
  for (int i = 0; i < length; i++) {
    command += (char)payload[i];
  }

  Serial.print("Mensaje recibido en el tópico [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(command);

  if (command == "forward") {
    Serial.println("Motor A Forward");
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, 255);  // ~78% speed

    Serial.println("Motor B Forward");
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 255);

  } else if (command == "backward") {
    Serial.println("Comando: REVERSA");
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 255);

    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, 255);

  } else if (command == "left") {
    Serial.println("Comando: GIRAR IZQUIERDA");
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 255);
    digitalWrite(IN3, LOW); 
    digitalWrite(IN4, HIGH);
    analogWrite(ENB, 255);

  } else if (command == "right") {
    Serial.println("Comando: GIRAR DERECHA");
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(ENA, 255);
    digitalWrite(IN3, HIGH); 
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 255);
  } else if (command == "stop") {
    Serial.println("Comando: DETENER");
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(ENA, 0);
    digitalWrite(IN3, LOW); 
    digitalWrite(IN4, LOW);
    analogWrite(ENB, 0);
    
  } else if (command == "light_on") {
    Serial.println("Comando: ENCENDER LUZ");
    digitalWrite(LIGHT_PIN, HIGH);
  } else {
    Serial.println("Comando desconocido");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("Conectado al broker MQTT");
      client.subscribe("car/control");
      Serial.println("Suscrito al tópico: car/control");
    } else {
      Serial.print("Fallo, rc=");
      Serial.print(client.state());
      Serial.println(" Reintentando en 5 segundos...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(LIGHT_PIN, OUTPUT);
  digitalWrite(LIGHT_PIN, LOW);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  Serial.println("Setup completo");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
