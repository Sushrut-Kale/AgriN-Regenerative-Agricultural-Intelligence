#ifndef AGRISENSE_CONFIG_H
#define AGRISENSE_CONFIG_H

#include <stdint.h>

#ifndef AGRISENSE_FW_VERSION
#define AGRISENSE_FW_VERSION "2.0.0"
#endif

#define HARDWARE_PROFILE_NAME "ESP32-DevKit-V1-Standard"
#define HARDWARE_REVISION "REV_A"

// Timing Configurations (in milliseconds)
#define DEFAULT_SAMPLE_INTERVAL_MS      (60 * 1000)       // Sample sensors every 60 seconds
#define DEFAULT_TELEMETRY_INTERVAL_MS   (300 * 1000)      // Send telemetry every 5 minutes
#define DEFAULT_HEARTBEAT_INTERVAL_MS   (120 * 1000)      // Send heartbeat ping every 2 minutes
#define SENSOR_WARMUP_DELAY_MS          (2000)            // Allow analog sensors to stabilize

// Communication & Retries
#define WIFI_CONNECT_TIMEOUT_MS         (15000)
#define HTTP_REQUEST_TIMEOUT_MS         (10000)
#define MAX_FAILED_TRANSMISSIONS        (5)
#define RETRY_BACKOFF_INITIAL_MS        (5000)
#define RETRY_BACKOFF_MAX_MS            (60000)

// Storage & Buffer Limits
#define MAX_OFFLINE_BUFFER_RECORDS      (120)             // Up to 10 hours of buffered telemetry
#define MAX_MEASUREMENTS_PER_PACKET     (16)

// Power & Battery Management
#define BATTERY_VOLTAGE_MIN             (3.20f)           // Cut-off threshold
#define BATTERY_VOLTAGE_MAX             (4.20f)           // Fully charged Li-ion
#define BATTERY_LOW_WARNING_VOLTAGE     (3.45f)           // Low battery warning threshold

// Debug Serial Baud Rate
#define SERIAL_DEBUG_BAUD               (115200)

#endif // AGRISENSE_CONFIG_H
