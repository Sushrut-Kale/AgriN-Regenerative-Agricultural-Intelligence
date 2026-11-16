#include "authentication.h"

Authentication::Authentication(const std::string& device_id, const std::string& api_key)
    : m_device_id(device_id), m_api_key(api_key) {}

std::map<std::string, std::string> Authentication::getAuthHeaders() const {
    std::map<std::string, std::string> headers;
    headers["X-Device-ID"] = m_device_id;
    headers["X-API-Key"] = m_api_key;
    headers["Content-Type"] = "application/json";
    headers["User-Agent"] = "AgriSense-ESP32-Client/2.0.0";
    return headers;
}

void Authentication::updateCredentials(const std::string& device_id, const std::string& api_key) {
    m_device_id = device_id;
    m_api_key = api_key;
}
