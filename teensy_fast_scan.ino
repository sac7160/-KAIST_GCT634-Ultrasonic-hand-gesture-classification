#include <Arduino.h>
#include <ADC.h>

#define SAMPLE_US      2                 // 2μs 간격
#define BUFFER_SIZE    32768             // 원형 버퍼 크기
#define HEADER_BYTE    0xAA

static ADC *adc = new ADC();
IntervalTimer samTimer;

volatile uint32_t ts_buf[BUFFER_SIZE];
volatile uint16_t val_buf[BUFFER_SIZE];
volatile uint16_t head = 0;
volatile uint16_t tail = 0;

void sampleISR() {
  uint16_t next = (head + 1) % BUFFER_SIZE;
  if (next == tail) tail = (tail + 1) % BUFFER_SIZE;

  ts_buf[head] = micros();
  val_buf[head] = adc->adc0->analogReadContinuous();
  head = next;
}

void setup() {
  Serial.begin(0);
  while (!Serial);

  adc->adc0->setAveraging(0);
  adc->adc0->setResolution(12);
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::VERY_HIGH_SPEED);
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::VERY_HIGH_SPEED);
  adc->adc0->startContinuous(A0);

  samTimer.begin(sampleISR, SAMPLE_US);
}

void loop() {
  while (tail != head) {
    if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == 'R') {
      noInterrupts();    // ISR 보호
      tail = (head - 1) % BUFFER_SIZE;      // 버퍼 초기화
      interrupts();
    }
  }

    if (Serial.availableForWrite() < 7) return;

    Serial.write(HEADER_BYTE);
    uint32_t ts = ts_buf[tail];
    uint16_t val = val_buf[tail];

    Serial.write((uint8_t *)&ts, 4);
    Serial.write(val >> 8);
    Serial.write(val & 0xFF);

    tail = (tail + 1) % BUFFER_SIZE;
  }
}
