#ifndef AGRISENSE_WIFI_MANAGER_H
#define AGRISENSE_WIFI_MANAGER_H

#include <string>
#include <stdint.h>

enum class WifiState {
    DISCONNECTED,
    CONNECTING,
    CONNECTED,
    FAILED
};

class WifiManager {
public:
    WifiManager(const std::string& ssid, const std::string& password);

    bool connect();
    void disconnect();
    bool isConnected() const;
    WifiState getState() const;
    int32_t getRssi() const;
    std::string getIpAddress() const;
    std::string getMacAddress() const;

private:
    std::string m_ssid;
    std::string m_password;
    WifiState m_state;
};

#endif // AGRISENSE_WIFI_MANAGER_H
