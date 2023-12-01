/*
  This code is for the control of the heaters for the In-Plane Thermal Conductivity Measurement Device
  designed by Ben Veghte, Aaron Leach, Rocco Tropea, Jordan Abi-Nader, and Charlie Schatmeyer. 
  This code was written specificaly with Power Distribution and Control PCB in mind with a raspberry pi pico
  however, utilizing other microcontrollers shouldn't require much change to this code.
  */
  //  AUTHOR: Ben Veghte

#include <Adafruit_INA260.h>
#include "RP2040_PWM.h" //Custom, not the library by Khoi Hoang due to it being archived and not tracking latest changes in Arduino Mbed OS RP2040 Boards, changes made using directions found here: https://forum.arduino.cc/t/library-rp2040-pwm-dont-compile/1168488/2 

// Communication Headers, see Serial Communication Pattern.md
#define HEATER_NOT_FOUND_ERROR 0x21
#define HEATER0_DC_HEADER 0x01
#define HEATER1_DC_HEADER 0x02
#define DUAL_DC_HEADER 0x03
#define HEATER0_INA260_HEADER 0x11
#define HEATER1_INA260_HEADER 0x12
#define TERMINATION 0xff


unsigned long timer_start; //variable to time how long operations take

float pwm_freq = 1100; //Hz


#define MSG_LEN 8
byte serial_rec_buf[MSG_LEN]; // For serial data coming in
byte serial_send_buf[MSG_LEN];

#define INA260_READ_PERIOD 2000 //In milliseconds. In order to read the current flowing through the heater, the mosfet needs to be in the on state and hitting the time in the duty cycle when the PWM is high is difficult without getting into the register and haven't figured out how to do that yet
unsigned long last_read = 0;

byte heaters_not_found;

unsigned long ina_mV;
unsigned long ina_mA;
float read_mA;


// Heater 0 Info
#define HEATER0 10 //not the GPxx number but the physical pin number
#define HEATER0_ALERT 9
Adafruit_INA260 heat0 = Adafruit_INA260();
float heat0_duty = 0;
RP2040_PWM* h0_pwm_inst;


// Heater 1 Info
#define HEATER1 12
#define HEATER1_ALERT 10
Adafruit_INA260 heat1 = Adafruit_INA260();
float heat1_duty = 0;
RP2040_PWM* h1_pwm_inst;



void setup() {
  //PWM Initialization
  //Pico can handle 8Hz - 62.5MHz, IRLB8721 maxes out around 4.8MHz due to delay time and rise time, doesn't work using arduino mbed OS RP2040
  pinMode(HEATER0, OUTPUT);
  pinMode(HEATER1, OUTPUT);

  // Serial Initialization
  Serial.begin(115200);
  while(!Serial){ // Wait for serial to be connected
    delay(1);
  }

  //INA Initialization
  //INA260 conversion time (the lenth the sensor averages over) needs to be as close to the period (or multiple periods) of the pwm_freq as possible to get an accuracte average for fault detection
  if (!heat0.begin(0x40)) {
    heaters_not_found = heaters_not_found&0B1;
  }
  if (!heat1.begin(0x41)) { 
    heaters_not_found = heaters_not_found&0B01;
    while(1);
  }
  if(heaters_not_found>0) { //If any heaters aren't found send error and then halt
    serial_send_buf[0] = HEATER_NOT_FOUND_ERROR;
    serial_send_buf[1] = heaters_not_found;
    serial_send_buf[MSG_LEN-1] = TERMINATION;
    Serial.write(serial_send_buf, MSG_LEN);
    memset(serial_send_buf, 0, MSG_LEN); // Empty the array for the next message to send
    while(1);
  }

  //If the code gets to this point, all heaters have been verified to be opertational
  //Set heater conversion time to match up with PWM frequency to ensure that we are getting the expected results
  heat0.setCurrentConversionTime(INA260_TIME_1_1_ms);
  heat0.setVoltageConversionTime(INA260_TIME_1_1_ms);
  heat1.setCurrentConversionTime(INA260_TIME_1_1_ms);
  heat1.setVoltageConversionTime(INA260_TIME_1_1_ms);

  //PWM Initialization
  //Pico can handle 8Hz - 62.5MHz, IRLB8721 maxes out around 4.8MHz due to delay time and rise time, doesn't work using arduino mbed OS RP2040
  h0_pwm_inst = new RP2040_PWM(HEATER0, pwm_freq, heat0_duty);
  h0_pwm_inst->setPWM();
  h1_pwm_inst = new RP2040_PWM(HEATER1, pwm_freq, heat1_duty);
  h1_pwm_inst->setPWM();

}

void loop() {
  //Handle Incoming serial data
  // Pyserial in the handler code is good at handling all sorts of data that the arduino can send
  // however the reverse isn't true, so going to in a standard form
  if (Serial.available() > 0) {
    serial_recv_handler();
  }
  if ((millis()-last_read)>INA260_READ_PERIOD) {
    last_read = millis();
    //Heater 0
    ina_mV = (unsigned long) heat0.readBusVoltage()*100;
    read_mA = heat0.readCurrent();
    ina_mA = (unsigned long) (read_mA <0 ) ? 0 : read_mA*100; //If current is negative, send 0, the negative current is really only sent when there is no current flowing and is an indicator of noise, and its so small we dont care
    serial_send_buf[0] = HEATER0_INA260_HEADER;
    serial_send_buf[1] = byte((ina_mV>>16));
    serial_send_buf[2] = byte((ina_mV>>8) );
    serial_send_buf[3] = byte(ina_mV );
    serial_send_buf[4] = byte(ina_mA>>16);
    serial_send_buf[5] = byte((ina_mA>>8) );
    serial_send_buf[6] = byte(ina_mA );
    serial_send_buf[MSG_LEN-1] = TERMINATION;
    Serial.write(serial_send_buf, MSG_LEN);
    
    //Heater 1
    ina_mV = (unsigned long) heat1.readBusVoltage()*100;
    read_mA = heat1.readCurrent();
    ina_mA = (unsigned long) (read_mA <0 ) ? 0 : read_mA*100;
    serial_send_buf[0] = HEATER1_INA260_HEADER;
    serial_send_buf[1] = byte((ina_mV>>16));
    serial_send_buf[2] = byte((ina_mV>>8) );
    serial_send_buf[3] = byte(ina_mV );
    serial_send_buf[4] = byte(ina_mA>>16);
    serial_send_buf[5] = byte((ina_mA>>8) );
    serial_send_buf[6] = byte(ina_mA );
    serial_send_buf[MSG_LEN-1] = TERMINATION;
    Serial.write(serial_send_buf, MSG_LEN);
  }

}

void serial_recv_handler() {
  Serial.readBytes(serial_rec_buf, MSG_LEN); //Reads MSG_LEN bytes sent by computer following format in Serial Communication Pattern.md
  // Serial.println("Received msg");
  switch (serial_rec_buf[0]) {
    case HEATER0_DC_HEADER: // Heater 0 Duty Cycle Change
      heat0_duty = float((((serial_rec_buf[1]<<8)|serial_rec_buf[2])<<8)|serial_rec_buf[3])*0.001;  
      h0_pwm_inst->setPWM(HEATER0, pwm_freq, heat0_duty);
      // Serial.print("Heater 0 Duty Cycle change to ");
      // Serial.println(heat0_duty);
      break;
    case HEATER1_DC_HEADER: //Heater 1 Duty Cycle Change
      heat1_duty = float((((serial_rec_buf[1]<<8)|serial_rec_buf[2])<<8)|serial_rec_buf[3])*0.001; 
      h1_pwm_inst->setPWM(HEATER1, pwm_freq, heat1_duty);
      // Serial.print("Heater 1 Duty Cycle change to ");
      // Serial.println(heat1_duty);
      break;
    case DUAL_DC_HEADER:
      heat0_duty = float((((serial_rec_buf[1]<<8)|serial_rec_buf[2])<<8)|serial_rec_buf[3])*0.001; 
      h0_pwm_inst->setPWM(HEATER0, pwm_freq, heat0_duty);
      // Serial.print("Heater 0 Duty Cycle change to ");
      // Serial.println(heat0_duty, 3);
      heat1_duty = float((((serial_rec_buf[4]<<8)|serial_rec_buf[5])<<8)|serial_rec_buf[6])*0.001; 
      h1_pwm_inst->setPWM(HEATER1, pwm_freq, heat1_duty);
      // Serial.print("Heater 1 Duty Cycle change to ");
      // Serial.println(heat1_duty, 3);


  }

}


