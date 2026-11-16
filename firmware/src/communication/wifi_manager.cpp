#include "wifi_manager.h"

#ifdef ARDUINO
#include <Arduino.h>
#include <WiFi.h>
#endif

WifiManager::WifiManager(const std::string& ssid, const std::string& password)
    : m_ssid(ssid),
      m_password(password),
      m_state(WifiState::DISCONNECTED) {}

bool WifiManager::connect() {
    if (m_ssid.empty()) {
        m_state = WifiState::FAILED;
        return false;
    }

#ifdef ARDUINO
    m_state = WifiState::CONNECTING;
    WiFi.mode(WIFI_STA);
    WiFi.begin(m_ssid.c_str(), m_password.c_str());

    uint32_t start = millis();
    while (WiFi.status() != WL_CONNECTED && (millis() - start < 15000)) {
        delay(250);
    }

    if (WiFi.status() == WL_CONNECTED) {
        m_state = WifiState::CONNECTED;
        return true;
    } else {
        m_state = WifiState::FAILED;
        return false;
    }
#else
    m_state = WifiState::CONNECTED;
    return true;
#endif
}

void WifiManager::disconnect() {
#ifdef ARDUINO
    WiFi.disconnect();
#endif
    m_state = WifiState::DISCONNECTED;
}

bool WifiManager::isConnected() const {
#ifdef ARDUINO
    return (WiFi.status() == WL_CONNECTED);
#else
    return (m_state == WifiState::CONNECTED);
#endif
}

WifiState WifiManager::getState() const {
    return m_state;
}

int32_t WifiManager::getRssi() const {
#ifdef ARDUINO
    if (isConnected()) {
        return WiFi.RSSI();
    }
    return -100;
#else
    return -65;
#endif
}

std::string WifiManager::getIpAddress() const {
#ifdef ARDUINO
    if (isConnected()) {
        return WiFi.localIP().toString().c_str();
    }
    return "0.0.0.0";
#else
    return "192.168.1.150";
#endif
}

std::string WifiManager::getMacAddress() const {
#ifdef ARDUINO
    return WiFi.macAddress().c_str();
#else
    return "24:6F:28:AB:CD:EF";
#endif
}
